# -*- coding: utf-8 -*-

def generate_sql_script(select_dict):
    if select_dict['city_name'] != None:
        city_sql = 'and city_name in ' + select_dict['city_name'] 
    else:
        city_sql = ''

    if select_dict['last_name'] != None:
        last_name_sql = select_dict['last_name']
    else:
        last_name_sql = ''

    if select_dict['first_name'] != None:
        first_name_sql = select_dict['first_name']
    else:
        first_name_sql = ''

    if select_dict['landlord'] != None:
        landlord_sql = 'and landlord in ' + select_dict['landlord']
    else:
        landlord_sql = ''

    if select_dict['phone_num'] != None:
        phone = select_dict['phone_num'].replace('[','"').replace(']','"')
        phone_num_sql = 'and phone_num in (' + phone + ')'
    else:
        phone_num_sql = ''

    if select_dict['gender_type'] != None:
        gender_type_sql = 'and gender_type in ' + select_dict['gender_type']
    else:
        gender_type_sql = ''
    
    sql = f'''SELECT * FROM cathay_db_kai.rent_house_info where {last_name_sql}{first_name_sql}{landlord_sql}{phone_num_sql}{gender_type_sql}{city_sql}'''

    if sql[-4:-1] == 'and':
        final_sql = sql[:-4]
    else:
        final_sql = sql.replace('where and', 'where')
        final_sql = final_sql.replace('"and', '" and')
        final_sql = final_sql.replace(')and', ') and')

    return final_sql