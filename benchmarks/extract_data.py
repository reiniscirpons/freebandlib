import glob
import json
import os

_output_dir = "./raw_benchmark_data/*/"


def read_benchmarks(bench_name):
    files = []
    directory = glob.glob(_output_dir)[0]
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if bench_name == "_".join(filename.split("_")[1:]).split(".")[0]:
            files.append(filename)

    results = []
    for file in files:
        with open(directory + file, "r") as in_file:
            data = json.load(in_file)
            if "benchmarks" in data:
                for benchmark in data["benchmarks"]:
                    name = benchmark["param"]
                    mean_time = benchmark["stats"]["mean"]
                    results.append((name, mean_time))

    return results


_data_dir = "./processed_benchmark_data/"


def write_tuples(bench_name, name1, data):
    with open(_data_dir + bench_name + "_" + name1 + ".dat", "w") as out_file:
        for t in data:
            t = " ".join(map(str, t))
            out_file.write(t + "\n")


from scipy.optimize import curve_fit


def line(x, a, b):
    return a * x + b


bench_name = "interval"
results_temp = read_benchmarks(bench_name)
results = []
for result in results_temp:
    name, mean_time = result
    alphabet_size = int(name.split("-")[0])
    word_length = int(name.split("-")[1])
    results.append((alphabet_size, word_length, mean_time))
results.sort()

results_x = {}
for x, y, z in results:
    if x not in results_x:
        results_x[x] = []
    results_x[x].append((y, z))
for x in results_x:
    results_x[x].sort()

results_y = {}
for x, y, z in results:
    if y not in results_y:
        results_y[y] = []
    results_y[y].append((x, z))
for y in results_y:
    results_y[y].sort()

results_p = []
for x, y, z in results:
    results_p.append((x * y, z))
results_p.sort()

# write_tuples(bench_name, "all", results)
write_tuples(bench_name, "benchmarks", results_p)
# for x in results_x:
# write_tuples(bench_name, "x_" + str(x), results_x[x])
# for y in results_y:
# write_tuples(bench_name, "y_" + str(y), results_y[y])
param, param_cov = curve_fit(
    line, [r[0] for r in results_p], [r[1] for r in results_p]
)
print(bench_name, param)


bench_name = "minimize"
results_temp = read_benchmarks(bench_name)
results = []
for result in results_temp:
    name, mean_time = result
    transducer_size = int(name.split("-")[0])
    results.append((transducer_size, mean_time))
results.sort()
write_tuples(bench_name, "benchmarks", results)
param, param_cov = curve_fit(
    line, [r[0] for r in results], [r[1] for r in results]
)
print(bench_name, param)

bench_name = "equal"
results_temp = read_benchmarks(bench_name)
results = []
for result in results_temp:
    name, mean_time = result
    word_len1 = int(name.split("-")[0])
    alph1 = int(name.split("-")[1])
    word_len2 = int(name.split("-")[2])
    alph2 = int(name.split("-")[3])
    results.append((word_len1, alph1, word_len2, alph2, mean_time))
results.sort()
results_p = []
for x, y, z, w, u in results:
    results_p.append(((x + z) * max(y, w), u))
results_p.sort()
results_binned = {}
for size, time in results_p:
    if size not in results_binned:
        results_binned[size] = []
    results_binned[size].append(time)
results_binned_mean = []
for size in results_binned:
    results_binned_mean.append(
        (size, sum(results_binned[size]) / len(results_binned[size]))
    )
results_binned_mean.sort()
write_tuples(bench_name, "benchmarks", results_p)
param, param_cov = curve_fit(
    line, [r[0] for r in results_p], [r[1] for r in results_p]
)
print(bench_name, param)

bench_name = "isomorphism"
results_temp = read_benchmarks(bench_name)
results = []
for result in results_temp:
    name, mean_time = result
    transducer_size = int(name.split("-")[0])
    results.append((transducer_size, mean_time))
results.sort()
write_tuples(bench_name, "benchmarks", results)
param, param_cov = curve_fit(
    line, [r[0] for r in results], [r[1] for r in results]
)
print(bench_name, param)

bench_name = "minword"
results_temp = read_benchmarks(bench_name)
results = []
for result in results_temp:
    name, mean_time = result
    transducer_size = int(name.split("-")[0])
    alphabet_size = int(name.split("-")[1])
    results.append((transducer_size, alphabet_size, mean_time))
results.sort()
# write_tuples(bench_name, "all", results)
results_p = []
for x, y, z in results:
    results_p.append((x * y, z))
results_p.sort()
write_tuples(bench_name, "benchmarks", results_p)
param, param_cov = curve_fit(
    line, [r[0] for r in results_p], [r[1] for r in results_p]
)
print(bench_name, param)

bench_name = "minimal_multiply"
results_temp = read_benchmarks(bench_name)
results = []
for result in results_temp:
    name, mean_time = result
    alphabet_size = int(name.split("-")[0])
    transducer1_size = int(name.split("-")[1])
    transducer2_size = int(name.split("-")[2])
    results.append(
        (alphabet_size, transducer1_size, transducer2_size, mean_time)
    )
results.sort()
# write_tuples(bench_name, "all", results)
results_p = []
for x, y, z, w in results:
    results_p.append((x * x + y + z, w))
results_p.sort()
write_tuples(bench_name, "benchmarks", results_p)
param, param_cov = curve_fit(
    line, [r[0] for r in results_p], [r[1] for r in results_p]
)
print(bench_name, param)

bench_name = "interval_multiply"
results_temp = read_benchmarks(bench_name)
results = []
for result in results_temp:
    name, mean_time = result
    alphabet_size = int(name.split("-")[0])
    transducer1_size = int(name.split("-")[1])
    transducer2_size = int(name.split("-")[2])
    results.append(
        (alphabet_size, transducer1_size, transducer2_size, mean_time)
    )
results.sort()
# write_tuples(bench_name, "all", results)
results_p = []
for x, y, z, w in results:
    results_p.append((x * x + y + z, w))
results_p.sort()
write_tuples(bench_name, "benchmarks", results_p)
param, param_cov = curve_fit(
    line, [r[0] for r in results_p], [r[1] for r in results_p]
)
print(bench_name, param)
