# Not used in the COGSCI23 submission
# VMP 2023-02-08: refactored and re-run.
include("configuration.jl")
using .cn, Printf, Statistics, Distributions, DelimitedFiles, CSV, DataFrames, IterTools, StatsBase, Chain, FStrings, Base.Threads

# manage paths 
dir = @__DIR__
path_configuration_probabilities = replace(dir, "analysis" => "data/preprocessing/configuration_probabilities.txt")
path_configurations = replace(dir, "analysis" => "data/preprocessing/configurations.txt")
path_entry_config = replace(dir, "analysis" => "data/preprocessing/entry_maxlikelihood.csv")

# load configurations and configuration probabilities
configuration_probabilities = readdlm(path_configuration_probabilities)
configurations = readdlm(path_configurations, Int)
configurations = cn.slicematrix(configurations)

# load all maximum likelihood configurations 
entry_maxlikelihood = DataFrame(CSV.File(path_entry_config))
config_ids = @chain entry_maxlikelihood begin _.config_id end
unique_configs = unique(config_ids) # think right, but double check 
unique_configs = unique_configs .+ 1 # because of 0-indexing in python 

# setup 
n_simulation = 10
n_timestep = 11 # first timestep is self 
global sample_list = [] 
global conf_list = []
total_configs = length(unique_configs)
@time begin 
global n_config = 0
global n_neighbors = 1
for unique_config in unique_configs
    global n_config += 1
    println("$n_config / $total_configs")
    for sim_number in 1:n_simulation
        x = findfirst(isequal(unique_config), [x for (x, y) in conf_list]) # is this what we want?
        if x isa Number 
            ConfObj = conf_list[x][2] # return the corresponding class 
        else 
            ConfObj = cn.Configuration(unique_config, configurations, configuration_probabilities)
        end 
        id = ConfObj.id 
        for time_step in 1:n_timestep
            push!(sample_list, [sim_number, time_step, id])
            if id ∉ [x for (x, y) in conf_list]
                push!(conf_list, [id, ConfObj]) 
            end 
            ConfObj = ConfObj.move(n_neighbors, conf_list)
            id = ConfObj.id 
        end 
    end 
    if n_config % 20 == 0
        println("saving file")
        df = DataFrame(
        simulation = [x for (x, y, z) in sample_list],
        timestep = [y for (x, y, z) in sample_list],
        config_id = [z-1 for (x, y, z) in sample_list] # -1 for python indexing
        )
        outpath = replace(dir, "analysis" => f"data/analysis/evo_raw/c{n_config}_nn{n_neighbors}_s_{n_simulation}_t_{n_timestep}")
        CSV.write(outpath, df)
        global sample_list = []
    end 
end 
end 