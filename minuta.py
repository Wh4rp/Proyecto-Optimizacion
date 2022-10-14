import pandas as pd
import numpy as np

def read_food(path):
    df = pd.read_csv(path)
    return df

def parser_dish_food(food):
    if type(food) is not str:
        return []
    else:
        return map(lambda x: x.strip().replace('.',''), food.split(','))

class AlimentationMonthly:
    def __init__(self, set_food, days, quantity):
        # key: day, value: dictionary of all food
        # with key: food, value: quantity
        self.set_food = set_food
        self.days = days
        self.quantity = quantity
        self.dictionary_food = {
            day: {
                food: 0
                for food in set_food
            }
            for day in range(1, self.days+1)
        }
    
    # Load foods from dataframe
    def load_foods(self, dataframe):
        for day in range(1, self.days+1):
            for type_food in dataframe.columns[1:]:
                for dish_food in parser_dish_food(dataframe.loc[day-1, type_food]):
                    # print('day: {}, dish food: {}'.format(day, dish_food))
                    for food in self.set_food:
                        if food in dish_food:
                            self.add_food(day, food)
    
    def add_food(self, day, food):
        self.dictionary_food[day][food] += self.quantity
    
    def __str__(self):
        # Only show foots with quantity > 0
        return str({
            day: {
                food: quantity
                for food, quantity in self.dictionary_food[day].items()
                if quantity > 0
            }
            for day in self.dictionary_food.keys()
        })
    
    # return dataframe pandas
    def to_dataframe(self):
        return pd.DataFrame(self.dictionary_food).T

def load_data(path_minuta, path_foods, path_school, days=31, quantity=1):
    df_foods = pd.read_csv(path_foods)
    df_minuta = pd.read_csv(path_minuta)
    set_foods = get_set_foods(df_foods)
    df_school = pd.read_csv(path_school)

    AM = AlimentationMonthly(set_foods, days, quantity)
    AM.load_foods(df_minuta)
    df_am = AM.to_dataframe()
    df_am.to_csv('minutas/{}-minuta.csv'.format(path_minuta.split('.')[0]))
    return (df_am, df_foods, df_school)

def get_set_foods(df):    
    return  set(df['ALIMENTO'].unique())