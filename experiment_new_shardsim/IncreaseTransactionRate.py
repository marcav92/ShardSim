import datetime
import os

DATE_DATA_POSITION = 3
DATA_DIRECTORY = "static_data"
OUTPUT_DATA_DIRECTORY = "processed_input_data/accelerated_dumps"
rates_per_second = [100, 200, 300]
CROSS_SHARD_TRANSACTION_RATIOS = [
    0.1,0.25,0.5
]


def modify_transaction_rate_of_file(input_file_path, output_file_path, rate_per_second):
    new_lines = []
    curr_time_obj = None

    with open(input_file_path, "r+") as f:
        for index, line in enumerate(f.readlines()):
            if index == 0:
                new_lines.append(line)
                continue

            line_array = line.split("\t")

            if index == 1:
                curr_time_obj = datetime.datetime.strptime(line_array[DATE_DATA_POSITION], "%Y-%m-%d %H:%M:%S")
                new_lines.append(line)
                continue

            if index % rate_per_second == 0:
                curr_time_obj = curr_time_obj + datetime.timedelta(seconds=1)

            line_array[DATE_DATA_POSITION] = curr_time_obj.strftime("%Y-%m-%d %H:%M:%S")

            new_lines.append("\t".join(line_array))

    with open(output_file_path, "w+") as f:
        for line in new_lines:
            f.write(line)

        f.close()


if __name__ == "__main__":
    rates_per_second = [100, 200, 300]
    os.makedirs(OUTPUT_DATA_DIRECTORY, exist_ok=True)
    



    for crossshard_transaction_ration in CROSS_SHARD_TRANSACTION_RATIOS:
        files = os.listdir(os.path.join(DATA_DIRECTORY,str(crossshard_transaction_ration)))
        for rate in rates_per_second:
            os.makedirs(f"{OUTPUT_DATA_DIRECTORY}/{str(crossshard_transaction_ration)}/{str(rate)}", exist_ok=True)
            for file in files:
                modify_transaction_rate_of_file(
                    f"{DATA_DIRECTORY}/{str(crossshard_transaction_ration)}/{file}",
                    f"{OUTPUT_DATA_DIRECTORY}/{str(crossshard_transaction_ration)}/{str(rate)}/{file.split('.')[0]}-rate-{rate}.tsv",
                    rate,
                )
