import copy

class Counter:
    counter = 0
    def increment(self):
        self.counter += 1
        return ''
    def set_to_zero(self):
        self.counter = 0
        return ''

def digits_to_readable_property_list(property_to_display: dict):
    property_to_display_changed = copy.deepcopy(property_to_display)
    for k, v in property_to_display.items():
        property_to_display_changed[k]['price'] = digits_to_str(v['price'])
    return property_to_display_changed

def digits_to_readable_distribution_property(distribution_property: dict):
    distribution_property_changed = copy.deepcopy(distribution_property)
    for k, v in distribution_property.items():
        distribution_property_changed[k]['price'] = digits_to_str(v['price'])
        count = 0
        for i in v['owners']:
            if 'личная доля в деньгах' in i:
                distribution_property_changed[k]['owners'][count]['личная доля в деньгах'] = digits_to_str(i['личная доля в деньгах'])
            if 'совместная доля в деньгах' in i:
                distribution_property_changed[k]['owners'][count]['совместная доля в деньгах'] = digits_to_str(i['совместная доля в деньгах'])
            count += 1
    return distribution_property_changed

def digits_to_readable_money_sum(money_sum: dict):
    money_sum_changed = copy.deepcopy(money_sum)
    for k, v in money_sum.items():
        money_sum_changed[k] = digits_to_str(v)
    return money_sum_changed

def digits_to_str(digit: int):
    digit_str = str(digit)
    new_str = ''
    temp = digit_str[::-1]
    while len(temp) > 3:
        new_str += temp[0:3]
        new_str += ' '
        temp = temp[3:]
    new_str += temp
    new_str = new_str[::-1]
    return new_str