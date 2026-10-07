# APS Marimo Latency Note

The interactive cross-correlation slider can feel laggy if you drag it continuously.
This is expected for the current teaching version: each slider update re-runs a
matplotlib redraw, and some nearby demonstration cells also generate relatively
large correlation plots.

For smooth use during lab, click the desired slider position instead of dragging
the handle. The computational lab functions themselves are not intentionally slow;
the latency is caused by reactive plotting work in the visualization.

