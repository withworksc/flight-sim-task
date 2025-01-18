import random
from collections import Counter

def generate_vertical_command(init_value):
    ver_vec = ['Climb', 'Descend']
    command_type = random.choice(ver_vec)
    if command_type == 'Climb':
        # calculate maximum alt（alt no greater than 38000 ft and the magnititude is not greater than 3000ft）
        max_climb = min((38000 - init_value['alt']) // 500, 6)  # 6*500 = 3000ft
        min_climb = 1  # 1*500 = 500ft
        if max_climb < min_climb:
            ver_ft = 0
        else:
            ver_ft = random.randint(min_climb, max_climb) * 500
    else:
        # calculate minimum alt（alt no less than 2500 ft and the magnititude is not greater than 3000ft）
        max_descend = min((init_value['alt'] - 2500) // 500, 6)  # 6*500 = 3000ft
        min_descend = 1  # 1*500 = 500ft
        if max_descend < min_descend:
            ver_ft = 0
        else:
            ver_ft = -random.randint(min_descend, max_descend) * 500
    
    return {'type': 'vertical', 'command': f'{command_type} {abs(ver_ft)} feet from current altitude.', 'action': command_type}

def generate_turn_command(x = None):
    trn_vec = ['left', 'right']
    
    if random.random() < 0.2:
        bank = 45
        trn_deg = random.randint(12, 18) * 10
        direction = random.choice(trn_vec)
        return {'type': 'turn', 'command': f'Steep turn {direction} {trn_deg} degrees from current heading.', 'direction': direction}
    else:
        bank_angles = [10, 20, 25, 30]
        bank = random.choice(bank_angles)
        trn_deg = random.randint(3, 18) * 10
        direction = random.choice(trn_vec)
        return {'type': 'turn', 'command': f'Turn {direction} {trn_deg} degrees from current heading with {bank}° bank angle.', 'direction': direction}

def generate_velocity_command(init_value, prev_velocity_command=None):
    if prev_velocity_command is None:
        velocity_vec = ['Accelerate', 'Decelerate']
        command_type = random.choice(velocity_vec)
        
        if command_type == 'Accelerate':
            max_increase = min((330 - init_value['velocity']) // 10, 10)
            min_increase = 2
            if max_increase < min_increase:
                velocity_kt = init_value['velocity']
            else:
                velocity_kt = init_value['velocity'] + random.randint(min_increase, max_increase) * 10
        else:
            max_decrease = min((init_value['velocity'] - 160) // 10, 10)
            min_decrease = 2
            if max_decrease < min_decrease:
                velocity_kt = init_value['velocity']
            else:
                velocity_kt = init_value['velocity'] - random.randint(min_decrease, max_decrease) * 10
    else:
        prev_velocity = int(prev_velocity_command['command'].split()[-2])
        
        if prev_velocity_command['action'] == 'Accelerate':
            command_type = 'Decelerate'
            max_decrease = min((prev_velocity - 160) // 10, 10)
            min_decrease = 2
            if max_decrease < min_decrease:
                velocity_kt = prev_velocity
            else:
                velocity_kt = prev_velocity - random.randint(min_decrease, max_decrease) * 10
        else:
            command_type = 'Accelerate'
            max_increase = min((330 - prev_velocity) // 10, 10)
            min_increase = 2
            if max_increase < min_increase:
                velocity_kt = prev_velocity
            else:
                velocity_kt = prev_velocity + random.randint(min_increase, max_increase) * 10
    
    return {'type': 'velocity', 'command': f'{command_type} to {velocity_kt} knots.', 'action': command_type}


def arrange_commands(commands):
    """
    logic：
    1. check if there are triple commands. if affirmative, then put them in #1, #3, #5
    2. if not, reorder the commands and avoid consecutive commands 
    """
    
    type_count = Counter(cmd['type'] for cmd in commands)
    
    
    triple_type = next((cmd_type for cmd_type, count in type_count.items() if count >= 3), None)
    
    if triple_type:
        # if there are triple commands, put them in #1, #3, #5
        same_type_cmds = [cmd for cmd in commands if cmd['type'] == triple_type][:3]
        other_cmds = [cmd for cmd in commands if cmd['type'] != triple_type]
        
        result = [None] * 5
        result[0] = same_type_cmds[0]  
        result[2] = same_type_cmds[1]  
        result[4] = same_type_cmds[2]  
        
        # for #2 and #4, the commands are random
        random.shuffle(other_cmds)
        result[1] = other_cmds[0]  
        result[3] = other_cmds[1]  
        
        return result
    else:
        # reorder the commands and avoid consecutive commands 
        result = []
        remaining = commands.copy()
        
        first_cmd = random.choice(remaining)
        result.append(first_cmd)
        remaining.remove(first_cmd)
        
        # remaining commands
        while remaining:
            valid_cmds = [cmd for cmd in remaining if cmd['type'] != result[-1]['type']]
            next_cmd = random.choice(valid_cmds)
            result.append(next_cmd)
            remaining.remove(next_cmd)
        
        return result

def generate_commands(init_value):
    
    random_commands = random.choice([
            lambda: generate_vertical_command(init_value),
            lambda: generate_velocity_command(init_value),
            lambda: generate_turn_command()
        ])

    commands = []

    commands.append(generate_velocity_command(init_value))
    commands.append(generate_vertical_command(init_value))
    commands.append(generate_turn_command())
    
    commands.append(random_commands())
    commands.append(random_commands())

    new_commands = arrange_commands(commands)
    
    # print([x['type'] for x in new_commands])

    return new_commands

def update_init_value(current_value, commands):
    """update params"""

    new_value = {
        'alt': current_value['alt'],
        'hdg': current_value['hdg'],
        'velocity': current_value['velocity']
    }

    for command in commands:

        if command['type'] == 'vertical':
            feet = int(command['command'].split()[1])
            if command['action'] == 'Climb':
                new_value['alt'] += feet
            else:  # Descend
                new_value['alt'] -= feet

        elif command['type'] == 'turn':
            degrees = int(next(word for word in command['command'].split() if word.isdigit()))
            old_hdg = new_value['hdg']
            if 'right' in command['command'].lower():
                new_value['hdg'] = (old_hdg + degrees) % 360
            else:  # left turn
                new_value['hdg'] = ((old_hdg - degrees) % 360 + 360) % 360

        elif command['type'] == 'velocity':
            new_value['velocity'] = int(command['command'].split()[-2])

    return new_value


# if __name__ == '__main__':
#     init_value = {
#         'alt': 10000,
#         'hdg': 360,
#         'velocity': 250
#         }
    
#     i = 0
#     while i < 2:
#         command_txt = generate_commands(init_value)
#         init_value = update_init_value(init_value, command_txt)
#         i += 1

