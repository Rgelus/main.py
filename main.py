import os
import numpy as np
import pandas as pd
import re
import datetime


# функция считывания по строкам полного номера таблицы
def group_work_process(data_array):
    tree_name = np.zeros(6, dtype=int)
    regex = r'\.|-'
    search_obj = re.split(regex, str(data_array[first_index_price(data_array)]))
    tree_name[0] = int(search_obj[0])
    tree_name[1] = int(search_obj[1])
    tree_name[5] = int(search_obj[2])
    for i in range(len(data_array)):
        for temp_tree in tree_names_dict:
            if temp_tree in str(data_array[i]):
                regex = r'\d\D*$'
                search_obj = re.search(regex, str(data_array[i]))
                regex = r'\.|-'
                search_elem = re.split(regex, search_obj.group())
                tree_name[tree_names_dict[temp_tree]] = int(search_elem[0])
                break
    group_work_process_num = tree_num(tree_name)
    return group_work_process_num


# функция построения
def tree_num(tree_name):
    s = str(tree_name[0]) + '.' + str(tree_name[1]) + '-' + str(tree_name[2]) + '-' + str(tree_name[3]) + \
        '-' + str(tree_name[4]) + '-' + str(tree_name[5])
    return s


# получение первого индекса расценок
def first_index_price(data_array):
    k = len(data_array)
    for i in range(len(data_array)):
        if 'Измеритель' in str(data_array[i]):
            k = i + 1
            break
    return k


# получение единиц измерений для расценки
def unit_of_measure(string_with_measure):
    regex = r'\d{1,}.*$'
    search_obj = re.search(regex, string_with_measure)
    unit = search_obj.group()
    return unit


# первый индекс списка состава работ
def first_index_labour_list(df):
    ll = 0
    flag = False
    for i in range(0, len(df.iloc[:, 0])):
        if df.iloc[i, 0] == 'Состав работ:':
            flag = True
            ll = i + 1
            break
    return ll, flag


# первый индекс начала кодов и ресурсов
def first_index_code(df):
    ll, flag = first_index_labour_list(df)
    fi_code = ll
    for i in range(ll, len(df.iloc[:, 0])):
        if df.iloc[i, 0] == 'Шифр\nресурса':
            fi_code = i
            break
    return fi_code


# преобразование названия для списка состава работ
def get_title_activity(string):
    regex = r'\.\s.{1,}'
    temp_title = re.search(regex, string).group()
    temp_title = temp_title[2:]
    return temp_title


# получение номера work process
def get_name_activity(string):
    regex = r'\n'
    name_list = re.split(regex, string)
    if len(name_list) == 1:
        name = name_list
    else:
        finite = []
        name = []
        regex = r'\d{1,}$'
        for temp_n in name_list:
            search_obj = re.search(regex, temp_n).group()
            finite.append(search_obj)
        regex = r'\d{1,}\.\d{1,}-\d{1,}-'
        for i in range(int(finite[0]), int(finite[1]) + 1):
            name.append(re.search(regex, name_list[0]).group() + str(i))
    return name


def code_search_iter(df, t_pres):
    for j in range(0, len(df.iloc[:, 0])):
        if df.iloc[j, 0] == 'Шифр\nресурса':
            t_k = j
            for p in range(1, len(df.iloc[t_k, :])):
                if df.iloc[t_k, p] == 'Наименование статей затрат, ресурсов':
                    t_m_name = p
                if df.iloc[t_k, p] == t_pres:
                    t_m = p
                    return t_k, t_m, t_m_name


# формирование первого листа склейки - с расценками
def work_process_sheet(df, gwp, df_rate):
    fip_num = first_index_price(df.iloc[:, 0])
    uom = unit_of_measure(df.iloc[(fip_num - 1), 0])
    length_of_frame = len(df.iloc[:, 0])
    pressmark, title, gwp_array, uom_array = [], [], [], []
    # dir_cost, salary, opera_of_mach, drive_salary = [], [], [], []
    # mat_cost, fix_time

    for i in range(fip_num, length_of_frame):
        if pd.isnull(df.iloc[i, 0]):
            break
        else:
            pressmark.append(df.iloc[i, 0])
            title.append(df.iloc[i, 1])
            gwp_array.append(gwp)
            uom_array.append(uom)

    rate_work = []
    wrate_work = []

    for i in range(0, len(pressmark)):
        flag = True
        for j in range(0, len(df_rate.iloc[:, 0])):
            if df_rate.iloc[j, 0] != ' ' and not(pd.isnull(df_rate.iloc[j, 0])):
                if df_rate.iloc[j, 0][1:] == pressmark[i]:
                    rate_work.append(str(df_rate.iloc[j, 10]))
                    wrate_work.append(str(df_rate.iloc[j, 12]))
                    break
                    flag = False
        if flag:
            print('шифр ', pressmark[i], ' не найден')

    soil_vol, soil_mass = np.zeros(len(pressmark)), np.zeros(len(pressmark))
    debris_mass, mach_mass = np.zeros(len(pressmark)), np.zeros(len(pressmark))
    mat_mass = np.zeros((len(pressmark)))

    dir_cost, salary = np.zeros(len(pressmark)), np.zeros(len(pressmark))
    opera_of_mach, drive_salary = np.zeros(len(pressmark)), np.zeros(len(pressmark))
    mat_cost, fix_time = np.zeros(len(pressmark)), np.zeros(len(pressmark))

    for temp_pres in range(0, len(pressmark)):
        k, m, m_name = code_search_iter(df, pressmark[temp_pres])
        for i in range(k+1, len(df.iloc[:, 0])):
            if df.iloc[i, 0] != 'Шифр\nресурса':
                try:
                    if df.iloc[i, m] == '-':
                        df.iloc[i, m] = 0
                    if df.iloc[i, m_name] == 'Прямые затраты:':
                        dir_cost[temp_pres] = df.iloc[i, m]
                    elif df.iloc[i, m_name] == 'заработная плата рабочих':
                        salary[temp_pres] = df.iloc[i, m]
                    elif df.iloc[i, m_name] == 'эксплуатация машин':
                        opera_of_mach[temp_pres] = df.iloc[i, m]
                    elif df.iloc[i, m_name] == 'в том числе заработная плата машинистов':
                        drive_salary[temp_pres] = df.iloc[i, m]
                    elif df.iloc[i, m_name] == 'материальные ресурсы':
                        mat_cost[temp_pres] = df.iloc[i, m]
                    elif df.iloc[i, m_name] == 'Затраты труда рабочих':
                        fix_time[temp_pres] = df.iloc[i, m]
                except IndexError:
                    break
            else:
                break

        for i in range(k+1, len(df.iloc[:, 0])):
            if df.iloc[i, 0] != 'Шифр\nресурса':
                if df.iloc[i, m_name] == 'Масса оборудования':
                    mach_mass[temp_pres] = df.iloc[i, m]
                elif df.iloc[i, m_name] == 'Масса мусора':
                    debris_mass[temp_pres] = df.iloc[i, m]
                elif df.iloc[i, m_name] == 'Масса материалов':
                    mat_mass[temp_pres] = df.iloc[i, m]
                elif df.iloc[i, m_name] == 'Масса земли':
                    soil_mass[temp_pres] = df.iloc[i, m]
                elif df.iloc[i, m_name] == 'Объем земли':
                    soil_vol[temp_pres] = df.iloc[i, m]
            else:
                break

    result = pd.DataFrame({'GROUP_WORK_PROCESS': gwp_array, 'PRESSMARK': pressmark,
                           'TITLE': title, 'UNIT_OF_MEASURE': uom_array,
                           'DIRECT_COSTS': dir_cost, 'SALARY': salary, 'OPERATION_OF_MACHINES': opera_of_mach,
                           'DRIVER_SALARY': drive_salary, 'COST_OF_MATERIAL': mat_cost, 'FIXED_TIME': fix_time,
                           'RATE_WORK_PROCESS': rate_work, 'WRATE_WORK_PROCESS': wrate_work, 'SOIL_VOL': soil_vol,
                           'SOIL_MASS': soil_mass, 'DEBRIS_MASS': debris_mass, 'MACHINES_MASS': mach_mass,
                           'MATERIAL_MASS': mat_mass})
    return result


# формирование второго листа склейки со списком работ
def activity_sheet(df):
    ll, flag = first_index_labour_list(df)
    work_process = []
    position = []
    title = []
    if flag:
        i = ll
        final = first_index_code(df) - 1
        while i < final:
            if not(pd.isnull(df.iloc[i, 0])):
                work_process_name = get_name_activity(df.iloc[i, 0])
                j = 1
                while i + j < final and pd.isnull(df.iloc[i+j, 0]):
                    j += 1
                for work_process_name_tp in work_process_name:
                    for k in range(i, i+j):
                        work_process.append(work_process_name_tp)
                        position.append(k-i+1)
                        title.append(get_title_activity(df.iloc[k, 1]))
                i = i + j
    result = pd.DataFrame({'WORK_PROCESS': work_process, 'POSITION': position, 'TITLE': title})
    return result


# формирование третьего листа склейки - список ресурсов
def resources_sheet(df):
    resource_flag = []
    work_process = []
    position = []
    title = []
    unit_measure = []
    expenditure = []

    fip_num = first_index_price(df.iloc[:, 0])
    length_of_frame = len(df.iloc[:, 0])
    pressmark = []

    for i in range(fip_num, length_of_frame):
        if pd.isnull(df.iloc[i, 0]):
            break
        else:
            pressmark.append(df.iloc[i, 0])

    for temp_pres in range(0, len(pressmark)):
        k, m, m_name = code_search_iter(df, pressmark[temp_pres])

        for i in range(0, len(df.iloc[k, :])):
            if df.iloc[k, i] == 'Ед. изм.':
                m_uom = i
                break

        for i in range(k+1, len(df.iloc[:, 0])):
            # print(df.iloc[i, 0])
            if df.iloc[i, 0] == 'Шифр\nресурса':
                break
            if not(pd.isnull(df.iloc[i, 0])):
                try:
                    if not((pd.isnull(df.iloc[i, 0])) or (df.iloc[i, m] == '-') or (df.iloc[i, m] == 0)
                           or (pd.isnull(df.iloc[i, m]))):
                        position.append(df.iloc[i, 0])
                        work_process.append(pressmark[temp_pres])
                        title.append(df.iloc[i, m_name])
                        unit_measure.append(df.iloc[i, m_uom])
                        expenditure.append(df.iloc[i, m])
                        resource_flag.append(0)
                except IndexError:
                    print('skip')

    result = pd.DataFrame({'WORK_PROCESS': work_process, 'PRESSMARK': position, 'TITLE': title,
                           'UNIT_OF_MEASURE': unit_measure, 'EXPENDITURE': expenditure,
                           'OTHER_RESOURCE_FLAG': resource_flag})
    return result


# формирование таблицы дерева склейки
def tables_sheet(gwp, df_tree):
    regex = r'^\d{1,}\.\d{1,}'
    regex_2 = r'-\d{1,}$'
    pressmark = re.search(regex, gwp).group() + re.search(regex_2, gwp).group()
    title = 'error'
    for i in range(0, len(df_tree.iloc[:, 1])):
        if df_tree.iloc[i, 1] == gwp:
            title = df_tree.iloc[i, 2]
    result = pd.DataFrame({'GROUP_WORK_PROCESS': [gwp], 'PRESSMARK': [pressmark], 'TITLE': [title]})
    return result


# вспомогательный словарь для определения полного названия таблицы
tree_names_dict = {
    'Отдел': 2,
    'Раздел': 3,
    'Подраздел': 4,
}

# Блок вступления программы, для описания происходящего в консоль
print('Исходные файлы, используемые в склейке, следует поместить в папку \\source. '
      'Готовые склейки файлов следует искать в папке \\results')

text_input = input('Запустить склейку? Напишите - yes \n')

if text_input == 'yes':
    # основная программа
    cwd = os.getcwd()
    tree_path = cwd + '\\tree'
    tree_path_file = tree_path + '\\' + os.listdir(tree_path)[0]

    rate_path = cwd + '\\rate_old_source'
    rate_path_file = rate_path + '\\' + os.listdir(rate_path)[0]

    full_rate_read_frame = pd.read_excel(rate_path_file, sheet_name=0)

    full_tree_read_frame = pd.read_excel(tree_path_file, sheet_name=0)

    source_path = cwd + '\\source'
    all_source_files_names = os.listdir(source_path)

    result_work_process_sheet = pd.DataFrame({})
    result_activity_sheet = pd.DataFrame({})
    result_resource_sheet = pd.DataFrame({})
    result_tables_sheet = pd.DataFrame({})

    for file_name in all_source_files_names:
        source_path_temp = source_path + '\\' + file_name
        xl = pd.ExcelFile(source_path_temp)
        sheet_names = xl.sheet_names
        open_name = sheet_names[-1]
        for temp_name in sheet_names:
            if 'Таб.' in temp_name:
                open_name = temp_name
                break
        data_read_frame = pd.read_excel(source_path_temp, sheet_name=open_name)

        try:
            GWP_num = group_work_process(data_read_frame.iloc[:, 0])

            temp_work_process_sheet = work_process_sheet(data_read_frame, GWP_num, full_rate_read_frame)
            temp_activity_sheet = activity_sheet(data_read_frame)
            temp_resources_sheet = resources_sheet(data_read_frame)
            temp_tables_sheet = tables_sheet(GWP_num, full_tree_read_frame)

            result_work_process_sheet = pd.concat([result_work_process_sheet,
                                                   temp_work_process_sheet], sort=False, axis=0)
            result_activity_sheet = pd.concat([result_activity_sheet, temp_activity_sheet], sort=False, axis=0)
            result_resource_sheet = pd.concat([result_resource_sheet, temp_resources_sheet], sort=False, axis=0)
            result_tables_sheet = pd.concat([result_tables_sheet, temp_tables_sheet], sort=False, axis=0)
        except Exception:
            print('Файл - {0}, прочитался с ошибками и не добавлен в итоговый'.format(file_name))

    # запись в файл полученных таблиц
    date_temp = datetime.datetime.now().strftime('%Y%m%d_%H%M')
    with pd.ExcelWriter('results\\glued_' + date_temp + '.xlsx', engine='xlsxwriter') as writer:
        result_work_process_sheet.to_excel(writer, sheet_name='WORK_PROCESS', index=False)
        result_activity_sheet.to_excel(writer, sheet_name='ACTIVITY', index=False)
        result_resource_sheet.to_excel(writer, sheet_name='RESOURCES', index=False)
        result_tables_sheet.to_excel(writer, sheet_name='TABLES', index=False)

    print('Процесс объединения завершен')
