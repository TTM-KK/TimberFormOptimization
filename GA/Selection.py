# -*- coding: utf-8 -*-
import rhinoscriptsyntax as rs
import random as rnd


def sort_low(sort_generate_instance_list):
    """
    :param sort_generate_instance_list: 評価値に合わせてソートされた個体を格納する空リスト
    :return:
    """
    flag = True
    while flag:
        counter = 0
        for i in range(len(sort_generate_instance_list)):
            value_a = sort_generate_instance_list[i].evaluation
            if i == len(sort_generate_instance_list) - 1:
                value_b = sort_generate_instance_list[0].evaluation
            else:
                value_b = sort_generate_instance_list[i + 1].evaluation


            if i == len(sort_generate_instance_list) - 1:
                if value_a < value_b:
                    sort_generate_instance_list[i], sort_generate_instance_list[0] = sort_generate_instance_list[0], sort_generate_instance_list[i]
                else:
                    counter = counter + 1
                    continue
            elif i != len(sort_generate_instance_list) - 1:
                if value_a > value_b:
                    sort_generate_instance_list[i], sort_generate_instance_list[i + 1] = sort_generate_instance_list[i + 1], sort_generate_instance_list[i]
                else:
                    counter = counter + 1
                    continue

        if counter == len(sort_generate_instance_list):
            flag = False

    list_evaluate_value = []
    for i in range(len(sort_generate_instance_list)):
        list_evaluate_value.append(sort_generate_instance_list[i].evaluation)

    # print("evaluate value: %s" % (list_evaluate_value))


def sort_high(sort_generate_instance_list):
    """
    :param sort_generate_instance_list: 評価値に合わせてソートされた個体を格納する空リスト
    :return:
    """
    flag = True
    while flag:
        counter = 0
        for i in range(len(sort_generate_instance_list)):
            value_a = sort_generate_instance_list[i].evaluation
            if i == len(sort_generate_instance_list) - 1:
                value_b = sort_generate_instance_list[0].evaluation
            else:
                value_b = sort_generate_instance_list[i + 1].evaluation


            if i == len(sort_generate_instance_list) - 1:
                if value_a > value_b:
                    sort_generate_instance_list[i], sort_generate_instance_list[0] = sort_generate_instance_list[0], sort_generate_instance_list[i]
                else:
                    counter = counter + 1
                    continue
            elif i != len(sort_generate_instance_list) - 1:
                if value_a < value_b:
                    sort_generate_instance_list[i], sort_generate_instance_list[i + 1] = sort_generate_instance_list[i + 1], sort_generate_instance_list[i]
                else:
                    counter = counter + 1
                    continue

        if counter == len(sort_generate_instance_list):
            flag = False

    list_evaluate_value = []
    for i in range(len(sort_generate_instance_list)):
        list_evaluate_value.append(sort_generate_instance_list[i].evaluation)

    # print("evaluate value: %s" % (list_evaluate_value))


def eliteSelection(elite_num, sort_generate_instance_list, select_elite_list):
    """
    :param elite_num: エリート選択を行う数
    :param sort_generate_instance_list: 評価値に合わせてソートされた個体が格納されているリスト
    :param select_elite_list: 選択された個体を格納する空リスト
    :return:
    """
    for i in range(elite_num):
        select = sort_generate_instance_list[i]
        select_elite_list.append(select)
    # if flag:
    # for i in range(elite_num):
    #     del sort_generate_instance_list[0]

def tournamentSelection_max(tournament_size, tournament_num, sort_generate_instance_list, select_tournament_list):
    for i in range(tournament_num):
        choices = rnd.sample(sort_generate_instance_list, tournament_size)
        # print("choices", choices)
        list_eva = []
        for j in range(len(choices)):
            list_eva.append(choices[j].evaluation)

        max_value = max(list_eva)
        max_value_index = list_eva.index(max_value)

        select_tournament_list.append(choices[max_value_index])


def tournamentSelection_min(tournament_size, tournament_num, sort_generate_instance_list, select_tournament_list):
    for i in range(tournament_num):
        choices = rnd.sample(sort_generate_instance_list, tournament_size)
        # print("choices", choices)
        list_eva = []
        for j in range(len(choices)):
            list_eva.append(choices[j].evaluation)

        min_value = min(list_eva)
        min_value_index = list_eva.index(min_value)

        select_tournament_list.append(choices[min_value_index])