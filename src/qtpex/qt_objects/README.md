# Readme

Classes which represent XY series (also line series and scatter series) which keeps a second scatter series to keep track of point ids.
It overrides the set configuration methods for the points to keep the same configurations even if points are deleted, or replaced, or intermediately inserted.

The default QT classes do not assign configurations to individual points, but their indices.
I.e., swapping points does not swap configurations, and we need additional functionality to keep track of the points configurations.

These classes handle such functionality.

Note: The overhead introduced is big!
Do not use these classes if you intend to have hundreds of points (or more) displayed in the scatter plot.
They are, however, useful for small number of points, e.g., in the transfer function example of qtpex.
