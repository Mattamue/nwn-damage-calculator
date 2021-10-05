from random import randint
from math   import floor

import pandas as pd
import matplotlib.pyplot as plt


#####################################################################
# DEFINES
ROUNDS = 500

WEAPON = {
    "name"                : "Dwaraxe SS",
    "damage"              : "1d10",
    "damage_bonus"        : 4 + 19,
    "threat_range"        : 19,
    "crit_multiplier"     : 3,
    "other_damage_bonus"  : [
        {"name" : "Positive", "damage" : 4, "resistable" : True},
        {"name" : "Divine", "damage" : "1d4", "resistable" : True},
        {"name" : "Fire", "damage" : "1d12", "resistable" : False},
        {"name" : "Cold", "damage" : "1d12", "resistable" : False}
    ]
}

CHARACTER = {
    "ab"                    : 48,
    "base_apr"              : 4,
    "dual_wielding"         : False,
    "extra_attack"          : 1, # haste, etc
    "overwhelming_critical" : False,
    "thundering_rage"       : False,
    "is_monk"               : False # If character is monk, AB penalty is set to -3 from -5 for consecutively attacks.
}

TARGET = {
    "ac_list"           : [20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70],
    "defensive_essence" : 5,  # if resistable is TRUE in other_damage_bonus elements, it will be reduced by this amount.
    "concealment"       : 50, # calculation will be done as assuming attacker has blind fight.
    "epic_dodge"        : False,
    "crit_immunity"     : False,
    "physical_immunity" : 0,
    "physical_damage_reduction": 0
}

RESULT_STR = ""

#####################################################################
# Helper Functions
def d(faces, rolls=1):
    if isinstance(faces, str):
        _rolls, _faces = parse_dice(faces)
        
        rolls *= _rolls
        faces  = _faces
    
    result = 0

    for _ in range(rolls):
        value = randint(1, faces)
        result += value

    return result

def parse_dice(dice="d6"):
    if isinstance(dice, int): return dice, 1

    split = dice.split("d")

    if split[0] == "":
        return 1, int(split[1])
    else:
        return int(split[0]), int(split[1])

def calculate_apr():
    global CHARACTER
    apr = CHARACTER["base_apr"]

    if CHARACTER["dual_wielding"]: apr += 2
    apr += CHARACTER["extra_attack"]

    return apr

def calculate_ab_from_attack_number(attack_number):
    global CHARACTER

    ab_penalty = 5

    if CHARACTER["is_monk"]: ab_penalty = 3

    if attack_number <= CHARACTER["base_apr"]:
        return CHARACTER["ab"] - (ab_penalty * (attack_number - 1))
    else:
        if CHARACTER["extra_attack"] > 0 \
        and attack_number <= CHARACTER["base_apr"] + CHARACTER["extra_attack"]:
            extra_atk_no = attack_number - CHARACTER["base_apr"] - CHARACTER["extra_attack"] + (CHARACTER["extra_attack"] - 1)
            ret_ab       = CHARACTER["ab"] - (extra_atk_no * ab_penalty)

            if CHARACTER["dual_wielding"]: ret_ab += 2

            return ret_ab
        elif  CHARACTER["dual_wielding"] \
        and attack_number <= calculate_apr():
            dw_atk_no = attack_number - calculate_apr() + 1
            return CHARACTER["ab"] - (dw_atk_no * ab_penalty)

    raise ValueError("error: cannot calculate ab from attack number, attack number: "+str(attack_number))

def get_weapon_damage(is_crit=False):
    global WEAPON

    roll_amount = 1
    if is_crit: roll_amount = WEAPON["crit_multiplier"]

    ret_val = d(WEAPON["damage"], roll_amount) + (WEAPON["damage_bonus"] * roll_amount)

    return ret_val

def get_weapon_other_damage(is_crit=False):
    global WEAPON

    ret_list = []

    for dmg_bonus in WEAPON["other_damage_bonus"]:
        roll_amount = 1
        if is_crit: roll_amount = WEAPON["crit_multiplier"]
        
        other_dmg = dmg_bonus.copy()
        
        dmg = d(str(dmg_bonus["damage"])+"d1" if isinstance(dmg_bonus["damage"], int) else dmg_bonus["damage"], roll_amount)

        other_dmg["damage"] = dmg
        ret_list.append(other_dmg)

    return ret_list

def calculate_percentage(val, max_val):
    return (100 * val) / max_val

def print_f(title="", text=""):
    global RESULT_STR

    if title == "" and text == "":
        RESULT_STR += "\n"
        print()
        return

    title_width = 35
    title_adjusted = title.ljust(title_width)

    RESULT_STR += title_adjusted + text + "\n"

    print(title_adjusted, end="")
    print(text, end="")
    print()

def apply_blind_fight(concealment):
    return (concealment ** 2) / 100

#####################################################################
# Main
print("---------------------------")
print("Zaphiel's Damage Calculator")
print("---------------------------\n")

print_f("ROUNDS", str(ROUNDS))
print_f()
print_f("WEAPON NAME", WEAPON["name"])
print_f("WEAPON DAMAGE", str(WEAPON["damage"]))
print_f("WEAPON DAMAGE BONUS", str(WEAPON["damage_bonus"]))
print_f("WEAPON THREAT RANGE", str(WEAPON["threat_range"]))
print_f("WEAPON CRITICAL HIT MULTIPLIER", str(WEAPON["crit_multiplier"]))
print_f("WEAPON OTHER DAMAGE BONUSES", "")
for dmg_bonus in WEAPON["other_damage_bonus"]:
    print_f("    * "+dmg_bonus["name"].upper(), str(dmg_bonus["damage"]))
print_f()
print_f("CHARACTER AB", str(CHARACTER["ab"]))
print_f("CHARACTER TOTAL APR", str(calculate_apr()))
print_f("CHARACTER IS MONK", str("Yes" if CHARACTER["is_monk"] else "No"))
print_f("CHARACTER OVERWHELMING CRITICAL", str("Yes" if CHARACTER["overwhelming_critical"] else "No"))
print_f("CHARACTER THUNDERING RAGE", str("Yes" if CHARACTER["thundering_rage"] else "No"))
print_f()
print_f("TARGET DEFENSIVE ESSENCE", str(TARGET["defensive_essence"]))
print_f("TARGET CONCEALMENT", str(TARGET["concealment"])+"% ({0:.2f}% w/ blind fight)".format(apply_blind_fight(TARGET["concealment"])))
print_f("TARGET EPIC DODGE", str("Yes" if TARGET["epic_dodge"] else "No"))
print_f("TARGET CRITICAL IMMUNITY", str("Yes" if TARGET["crit_immunity"] else "No"))
print_f("TARGET PHYSICAL IMMUNITY", str(TARGET["physical_immunity"])+"%")
print_f("TARGET PHYSICAL DAMAGE REDUCTION", str(TARGET["physical_damage_reduction"]))

example_result = {
    "total_attack"     : 0,
    "total_hit"        : 0,
    "total_miss"       : 0,
    "total_concealed"  : 0,
    "total_epic_dodge" : 0,
    "total_crit"       : 0,
    "total_damage"     : 0,
    "total_weapon_damage" : 0,
    "total_bonus_damage"  : None
}
result_list = {}

for _ in range(ROUNDS):
    epic_dodge_list = {}
    
    for target_ac in TARGET["ac_list"]:
        epic_dodge_list[target_ac] = True
    
    for i in range(calculate_apr()):
        for target_ac in TARGET["ac_list"]:
            if target_ac not in result_list:
                result_list[target_ac] = example_result.copy()
                result_list[target_ac]["total_bonus_damage"] = {}

            character_ab = calculate_ab_from_attack_number(i + 1)
            result_list[target_ac]["total_attack"] += 1

            is_hit   = False
            hit_roll = d(20)

            if  TARGET["concealment"] > 0 \
            and randint(1, 100) < apply_blind_fight(TARGET["concealment"]):
                # Target concealed
                result_list[target_ac]["total_concealed"] += 1
            elif (character_ab + hit_roll >= target_ac or hit_roll == 20) \
            and hit_roll != 1:
                is_hit = True
                
                if TARGET["epic_dodge"] \
                and epic_dodge_list[target_ac]:
                    # Epic Dodged
                    is_hit = False
                    epic_dodge_list[target_ac] = False
                    result_list[target_ac]["total_epic_dodge"] += 1

            weapon_damage = 0
            other_damage  = []

            if is_hit:
                is_critical = False

                # check if critical
                if not TARGET["crit_immunity"] \
                and hit_roll >= WEAPON["threat_range"] \
                and character_ab + d(20) >= target_ac: # confirmation roll
                    is_critical = True
                    result_list[target_ac]["total_crit"] += 1

                weapon_damage = get_weapon_damage(is_critical)
                other_damage  = get_weapon_other_damage(is_critical)
                
                if is_critical:
                    if CHARACTER["overwhelming_critical"]:
                        weapon_damage += d(6, WEAPON["crit_multiplier"])
                        
                    if CHARACTER["thundering_rage"]:
                        weapon_damage += d(6, 2)

                if TARGET["physical_immunity"] > 0:
                    weapon_damage -= floor(weapon_damage * TARGET["physical_immunity"] / 100)
                    
                if TARGET["physical_damage_reduction"] > 0:
                    weapon_damage -= TARGET["physical_damage_reduction"]
                    
                if weapon_damage < 0: weapon_damage = 0

                result_list[target_ac]["total_damage"] += weapon_damage
                result_list[target_ac]["total_weapon_damage"] += weapon_damage

                for dmg in other_damage:
                    if dmg["name"] not in result_list[target_ac]["total_bonus_damage"]:
                        result_list[target_ac]["total_bonus_damage"][dmg["name"]] = 0

                    adjusted_dmg = dmg["damage"]
                    
                    if TARGET["defensive_essence"] and dmg["resistable"]:
                        adjusted_dmg -= TARGET["defensive_essence"]

                    if adjusted_dmg < 0: adjusted_dmg = 0
                    else:
                        result_list[target_ac]["total_bonus_damage"][dmg["name"]] += adjusted_dmg
                        result_list[target_ac]["total_damage"] += adjusted_dmg
                
                result_list[target_ac]["total_hit"] += 1
                    
            else: # miss
                result_list[target_ac]["total_miss"] += 1

print_f("\n-=[RESULTS]=-")

results = sorted([(key, result_list[key]) for key in result_list])

# print(results)

"""
[(20, {'total_attack': 350, 'total_hit': 258, 'total_miss': 92, 'total_concealed': 75, 'total_epic_dodge': 0, 'total_crit': 27, 'total_damage': 10264, 'total_weapon_damage': 9032, 'total_bonus_damage': {'Divine': 92, 'Positive': 570, 'Negative': 570}}),
(25, {'total_attack': 350, 'total_hit': 252, 'total_miss': 98, 'total_concealed': 83, 'total_epic_dodge': 0, 'total_crit': 25, 'total_damage': 9915, 'total_weapon_damage': 8715, 'total_bonus_damage': {'Divine': 92, 'Positive': 554, 'Negative': 554}}),
(30, {'total_attack': 350, 'total_hit': 253, 'total_miss': 97, 'total_concealed': 81, 'total_epic_dodge': 0, 'total_crit': 30, 'total_damage': 10249, 'total_weapon_damage': 9014, 'total_bonus_damage': {'Divine': 103, 'Positive': 566, 'Negative': 566}}),
(35, {'total_attack': 350, 'total_hit': 250, 'total_miss': 100, 'total_concealed': 90, 'total_epic_dodge': 0, 'total_crit': 37, 'total_damage': 10260, 'total_weapon_damage': 8990, 'total_bonus_damage': {'Divine': 122, 'Positive': 574, 'Negative': 574}}),
(40, {'total_attack': 350, 'total_hit': 237, 'total_miss': 113, 'total_concealed': 89, 'total_epic_dodge': 0, 'total_crit': 25, 'total_damage': 9289, 'total_weapon_damage': 8147, 'total_bonus_damage': {'Divine': 94, 'Positive': 524, 'Negative': 524}}),
(45, {'total_attack': 350, 'total_hit': 209, 'total_miss': 141, 'total_concealed': 100, 'total_epic_dodge': 0, 'total_crit': 21, 'total_damage': 8198, 'total_weapon_damage': 7199, 'total_bonus_damage': {'Divine': 79, 'Positive': 460, 'Negative': 460}}),
(50, {'total_attack': 350, 'total_hit': 179, 'total_miss': 171, 'total_concealed': 81, 'total_epic_dodge': 0, 'total_crit': 22, 'total_damage': 7177, 'total_weapon_damage': 6304, 'total_bonus_damage': {'Divine': 69, 'Positive': 402, 'Negative': 402}}),
(55, {'total_attack': 350, 'total_hit': 123, 'total_miss': 227, 'total_concealed': 81, 'total_epic_dodge': 0, 'total_crit': 15, 'total_damage': 4939, 'total_weapon_damage': 4341, 'total_bonus_damage': {'Divine': 46, 'Positive': 276, 'Negative': 276}}),
(60, {'total_attack': 350, 'total_hit': 74, 'total_miss': 276, 'total_concealed': 80, 'total_epic_dodge': 0, 'total_crit': 8, 'total_damage': 2890, 'total_weapon_damage': 2524, 'total_bonus_damage': {'Divine': 38, 'Positive': 164, 'Negative': 164}}),
(65, {'total_attack': 350, 'total_hit': 28, 'total_miss': 322, 'total_concealed': 90, 'total_epic_dodge': 0, 'total_crit': 2, 'total_damage': 1097, 'total_weapon_damage': 971, 'total_bonus_damage': {'Divine': 6, 'Positive': 60, 'Negative': 60}}),
(70, {'total_attack': 350, 'total_hit': 16, 'total_miss': 334, 'total_concealed': 84, 'total_epic_dodge': 0, 'total_crit': 0, 'total_damage': 553, 'total_weapon_damage': 489, 'total_bonus_damage': {'Divine': 0, 'Positive': 32, 'Negative': 32}})]
"""

ac_list = []

for tuple_entry in results:
    ac_list.append(tuple_entry[0])

damage_list = []

for tuple_entry in results:
    damage_list.append(tuple_entry[1]['total_damage'] / tuple_entry[1]['total_attack'])

damage_data_df = pd.DataFrame(ac_list, columns=["AC"])

damage_data_df['Avg Dmg'] = damage_list

damage_data_df.set_index('AC').plot(kind='bar',title="Avg Dmg per AC")

plt.show()

# for target_ac, result in results:
#     print_f()
#     print_f("TARGET AC", str(target_ac))
#     print_f("TOTAL ATTACK", str(result["total_attack"]))
#     print_f("TOTAL HIT", str(result["total_hit"])+" ({0:.2f}% of total attacks)".format(calculate_percentage(result["total_hit"], result["total_attack"])))
#     print_f("TOTAL MISS", str(result["total_miss"])+" ({0:.2f}% of total attacks)".format(calculate_percentage(result["total_miss"], result["total_attack"])))
#     print_f("    * CONCEALED ATTACKS", str(result["total_concealed"])+" ({0:.2f}% of total misses)".format(calculate_percentage(result["total_concealed"], result["total_miss"])))
#     print_f("    * EPIC DODGE", str(result["total_epic_dodge"])+" ({0:.2f}% of total misses)".format(calculate_percentage(result["total_epic_dodge"], result["total_miss"])))
#     print_f("TOTAL CRITICAL HIT", str(result["total_crit"])+" ({0:.2f}% of total hits)".format(calculate_percentage(result["total_crit"], result["total_hit"])))
#     print_f()
#     print_f("TOTAL DAMAGE", str(result["total_damage"]))
#     print_f("TOTAL WEAPON DAMAGE", str(result["total_weapon_damage"])+" ({0:.2f}% of total damage)".format(calculate_percentage(result["total_weapon_damage"], result["total_damage"])))
#     print_f("TOTAL OTHER DAMAGE", str(result["total_damage"] - result["total_weapon_damage"])+" ({0:.2f}% of total damage)".format(calculate_percentage(result["total_damage"] - result["total_weapon_damage"], result["total_damage"])))
#     for name in result["total_bonus_damage"].keys():
#         dmg = result["total_bonus_damage"][name]
#         print_f("    * "+name.upper(), str(dmg))
#     print_f()
#     print_f("AVARAGE DAMAGE PER ROUND", "{0:.2f}".format(result["total_damage"] / ROUNDS))
#     print_f("\n"+"="*50)

# with open("result.txt", "w") as f:
#     f.write(RESULT_STR)
