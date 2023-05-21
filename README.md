# optComp
optComp is an open-source optimization module for fiber direction in composite structures. Is is based in CalculiX finite element program.

Current limitations:
- Only static linear analysis can be used
- All *ORIENTATIONS cards must be rectangular systems defined in sequence and without rotation
- All orientations will be optimized, user can not define non-optimized domains
- The orientations Z-axis must be correctly defined: Z-axis must be coincident with local Z-axis of the shell
- The input file must not include any *NODE PRINT or *EL PRINT cards
- Only 1 step is supported
- The nodes/elements sets must be defined previously
- The CalculiX executable must be placed within optComp folder or be acessible via PATH.
