## Perfetto Trace Script

Can be used to extract specific data from a perfetto trace file.

ScriptV2 is way more compact and efficient than the previous version and should always be used.

**ScriptV1 is deprecated and is just here for references.**

So far the metrics tracked are : 
- Power rails data
- Average frequency for the little CPU group
- Average frequency for the medium CPU group (big in the trace)
- Average frequency for the big CPU group (bigger in the trace)
- Frequency of the first GPU
- Frequency of the second GPU
- Average GPU memory frequency
- Battery discharge

Usage : 
```bash
cd ScriptV2
python3 main.py power_rails_slice       
```

power_rails_slice is mandatory, it's used to specify the range of the trace to analyze **FOR THE POWER RAILS ONLY**. 
No matter what the slice given is, other traced metrics will be for the entire trace.

The slice format is as follows 
```bash
[x:y]
```
Where x is the start of the slice and y is the end of the slice.
With x and y being integers and 0 <= x < y <= 100.


