import folium
import pandas as pd
import webbrowser
import os

# Загрузка данных из TXT файла с использованием пробелов в качестве разделителей
df = pd.read_csv("flight_data.txt", sep=r"\s+", header=0, names=["Time", "Year", "Month", "Day", "Latitude", "Longitude", "Altitude", "Speed"])

# Замена запятых на точки в столбцах Latitude и Longitude
df["Latitude"] = df["Latitude"].str.replace(',', '.').astype(float)
df["Longitude"] = df["Longitude"].str.replace(',', '.').astype(float)

# Преобразование столбца "Time" и создание столбца "Datetime"
df["Datetime"] = pd.to_datetime(df["Year"].astype(str) + '-' + df["Month"].astype(str) + '-' + df["Day"].astype(str) + ' ' + df["Time"], format="%Y-%m-%d %H:%M:%S,%f")

# Сортировка по времени
df = df.sort_values(by="Datetime")

# Создание карты
my_map = folium.Map(location=[df["Latitude"].mean(), df["Longitude"].mean()], zoom_start=12)

# Добавление маршрута
folium.PolyLine(
    locations=list(zip(df["Latitude"], df["Longitude"])),
    color="blue",
    weight=2.5,
    opacity=1,
).add_to(my_map)

# Добавление маркеров через каждую минуту
previous_time = None
for index, row in df.iterrows():
    if previous_time is None or (row["Datetime"] - previous_time).total_seconds() >= 1 * 60:  # 1 минута в секундах
        folium.Marker(
            location=[row["Latitude"], row["Longitude"]],
            popup=(
                f"<b>Дата:</b> {row['Datetime'].strftime('%d.%m.%Y')}<br>"
                f"<b>Время:</b> {row['Datetime'].strftime('%H:%M:%S')}<br>"
                f"<b>Скорость:</b> <span style='white-space: nowrap;'>{round(float(row['Speed'].replace(',', '.')), 1)} км/ч</span><br>"
                f"<b>Высота:</b> <span style='white-space: nowrap;'>{round(float(row['Altitude'].replace(',', '.')), 1)} м</span>"
            ),
            icon=folium.Icon(color="blue"),
        ).add_to(my_map)
        previous_time = row["Datetime"]

start_time = df["Datetime"].iloc[0].strftime("%d.%m.%Y Время: %H:%M:%S")
end_time = df["Datetime"].iloc[-1].strftime("%d.%m.%Y Время: %H:%M:%S")

folium.Marker(
    location=[df["Latitude"].iloc[0], df["Longitude"].iloc[0]],
    popup=f"<b>Начало: {start_time}<b>",
    icon=folium.Icon(color="green"),
).add_to(my_map)

folium.Marker(
    location=[df["Latitude"].iloc[-1], df["Longitude"].iloc[-1]],
    popup=f"<b>Конец: {end_time}<b>",
    icon=folium.Icon(color="red"),
).add_to(my_map)

# Сохранение карты
output_file = "Координаты полета.html"
my_map.save(output_file)

# Открытие карты в браузере
webbrowser.open('file://' + os.path.realpath(output_file))
