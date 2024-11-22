import csv


def import_to_csv(data, filename):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        current_idx = 0
        for i in data:
            for j in i["delta_list"]:
                writer.writerow([i["rail"], j])

