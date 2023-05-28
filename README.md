# optComp
The software **optComp** is an open-source optimization module for composite structures. Is is based in **CalculiX** finite element program.

## Current state:
At the moment, the backend is being developed and tests are being conducted, therefore no user available version is available yet. However, if you are interested in running the software now, please contact me and I can provide you test files and better descriptions on how to use the tool. The frontend will be fully developed after enough completion of the backend.

## Current limitations:
- Only CalculiX input files are supported
- Only orientations can be optimized
- Only shells can be optimized (maybe solids, but tests are not made for them yet)
- Only static linear analysis can be used
- All *ORIENTATIONS cards must be rectangular systems defined in sequence and without rotation
- All orientations will be optimized, user can not define non-optimized domains
- The orientations Z-axis must be correctly defined: Z-axis must be coincident with local Z-axis of the shell
- The input file must not include any *NODE PRINT or *EL PRINT cards
- Only 1 step is supported
- The nodes/elements sets must be defined previously
- The CalculiX executable must be placed within optComp folder or be acessible via PATH.

## Performance:
- Tests show that for small input files (~150 S8R elements) the results show that the optimizer takes almost 25% of the total runtime, the rest being CalculiX execution
- For slightly increased file size (~1500 S8R elements) the percentage drops to 5% of total runtime. This indicates that the optimizer does not take much processing at all when compared to FEM runtime as the model size grows.

## Future implementations:
- Cylindrical CSYS support
- Buckling and Frequency steps support
- Solid elements support (lacks enough tests)
- Number of layers as optimization variables
- Different materials as optimization variables
- Fiber angles as discrete variables (0°, 15°, 30° ... 90°)
- Thickness of core as optimization variable (for sandwich structures)
- Interative selector to make it easier to set the optimization parameters