# Independent raw-map -> full weighted-flag H1 calculation. No Python invocation.
using Ripserer
using JSON
using SHA
using Dates

const BASE = dirname(@__DIR__)

function run_record(record, mode)
    started = time()
    key = String(record["key"])
    n = Int(record["n"])
    path = joinpath(BASE, String(record["raw_path"]))
    bytes = read(path)
    raw_sha = bytes2hex(sha256(bytes))
    raw_sha == record["raw_sha256"] || error("Input hash mismatch: $key")
    ENDIAN_BOM == 0x04030201 || error("Runner requires little-endian host")
    length(bytes) == 8*n*n || error("Wrong input length: $key")
    raw = reshape(copy(reinterpret(Float64, bytes)), n, n)
    all(isfinite, raw) || error("Nonfinite map: $key")
    raw == transpose(raw) || error("Asymmetric map: $key")
    minimum_weight = Inf
    mean_sum = 0.0
    for j in 1:n, i in 1:j-1
        minimum_weight = min(minimum_weight, -raw[i,j])
        mean_sum += raw[i,j]
    end
    offset = max(0.0, 1.0 - minimum_weight)
    effective = zeros(Float32, n, n)
    for j in 1:n, i in 1:n
        if i != j
            effective[i,j] = Float32(-raw[i,j] + offset)
            isfinite(effective[i,j]) && effective[i,j] > 0 || error("Invalid edge: $key")
        end
    end
    effective_sha = bytes2hex(sha256(reinterpret(UInt8, vec(effective))))
    ph_started = time()
    result = ripserer(Rips(effective; threshold=Inf, sparse=false);
        dim_max=1, modulus=2, cutoff=0, reps=false, alg=:cohomology,
        verbose=false)
    ph_elapsed = time() - ph_started
    intervals = [(Float64(interval[1]) - offset, Float64(interval[2]) - offset)
                 for interval in result[2]]
    all(p -> isfinite(p[1]) && isfinite(p[2]) && p[1] < p[2], intervals) ||
        error("Nonfinite/nonpositive interval: $key")
    sort!(intervals)
    output = Matrix{Float64}(undef, length(intervals), 2)
    for (i, (b,d)) in enumerate(intervals)
        output[i,1] = b
        output[i,2] = d
    end
    outdir = joinpath(BASE, "outputs", mode)
    mkpath(outdir)
    outpath = joinpath(outdir, key * ".f64")
    write(outpath, reinterpret(UInt8, vec(output)))
    receipt = Dict(
        "key" => key, "status" => "completed", "n" => n,
        "raw_sha256" => raw_sha, "effective_sha256" => effective_sha,
        "offset" => offset, "mean" => mean_sum / (n*(n-1)/2),
        "interval_count" => length(intervals),
        "output_sha256" => bytes2hex(sha256(read(outpath))),
        "ph_seconds" => ph_elapsed, "elapsed_seconds" => time()-started,
        "julia_version" => string(VERSION), "ripserer_version" => string(pkgversion(Ripserer)),
        "algorithm" => "cohomology", "modulus" => 2, "threshold" => "Inf",
        "cutoff" => 0, "timestamp_utc" => string(now(UTC)),
    )
    write(joinpath(outdir, key * ".json"), JSON.json(receipt))
    println(JSON.json(receipt))
    flush(stdout)
    GC.gc()
end

function main()
    mode = ARGS[1]
    mode in ("controls", "genomic") || error("mode must be controls or genomic")
    manifest_name = mode == "controls" ? "control_runner_manifest.json" : "genomic_runner_manifest.json"
    records = JSON.parsefile(joinpath(BASE, "inputs", manifest_name))["records"]
    shard = length(ARGS) >= 2 ? parse(Int, ARGS[2]) : 1
    shards = length(ARGS) >= 3 ? parse(Int, ARGS[3]) : 1
    1 <= shard <= shards || error("Invalid shard")
    for (i, record) in enumerate(records)
        if mod(i-1, shards)+1 == shard
            run_record(record, mode)
        end
    end
end

main()
