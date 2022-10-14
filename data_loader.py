import pandas as pd
import numpy as np

def load_data(file_fs, file_foods, file_school, days=31, quantity=1):
    df_foods = pd.read_csv('data/{}'.format(file_fs))
    df_minuta = pd.read_csv('data/{}'.format(file_foods))
    df_school = pd.read_csv('data/{}'.format(file_school))

    set_foods = get_set_foods(df_foods)
    FS = AlimentationMonthly(set_foods, days, quantity)
    FS.load_foods(df_minuta)
    df_fs = FS.to_dataframe()
    df_fs.to_csv('data/{}_out.csv'.format(file_fs.split('.')[0]))
    return (df_fs, df_foods, df_school)

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

def get_set_foods(df):    
    return  set(df['ALIMENTO'].unique())