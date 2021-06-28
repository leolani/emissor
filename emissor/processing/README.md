# EMISSOR Dataset processing module

This module provides a small utility to create and process dataset in the EMISSOR format
based on user provided plugins. Plugins can provide implementations to *preprocess* data,
*initialize* EMISSOR metadata and *process* the data by adding new mentions and annotations
to signals.

The module can be executed with 

    python -m emissor.processing --plugins <plugin_path> --scenarios <data_path>

which will process the data set with the given plugin(s).

Optionally, the stages of processing can be specified explicitly as command line options and only the given stages are executed.
If none are specified, all of them will be executed. For a full list of options run

    python -m emissor.processing --help


## Plugin API

