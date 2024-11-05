import csv
import pandas as pd
from pathlib import Path
import asyncio


async def add_id_to_csv(file_name: str, new_id: int, status=None) -> bool:
    df = pd.read_csv(Path('src', 'data', f'{file_name}.csv'))
    # print(new_id in df['id'].tolist())
    if new_id in df['id'].tolist():
        return False
    # df.loc[len(df)] = pd.Series({'id': new_id})
    try:
        df.loc[len(df)] = pd.Series({'id': new_id, 'status': status})
    except:
        print('sloamlis tvoi kostyli ebanye')
    # print(df)
    df.to_csv(Path('src', 'data', f'{file_name}.csv'), index=False)
    return True


def convert_csv_id_to_array(file_name: str) -> list[str]:
    df = pd.read_csv(Path('src', 'data', f'{file_name}.csv'))
    arr = df['id'].tolist()
    return arr


def get_attr_from_csv(file_name: str, attr_name: str) -> str:
    df = pd.read_csv(Path('src', 'data', f'{file_name}.csv'), encoding='CP1251')
    current_attr = df[attr_name].values[0]
    return current_attr


async def set_attr_from_csv(file_name: str, attr_name: str, new_attr: str) -> None:
    df = pd.read_csv(Path('src', 'data', f'{file_name}.csv'), encoding='CP1251')
    df[attr_name] = new_attr
    df.to_csv(Path('src', 'data', f'{file_name}.csv'), index=False, encoding='CP1251')
