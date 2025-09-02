# tikzimg
Script for fast creation of latex tikz images.


- In python
- Available system wide
- command will be 'tikzimg'
- cli script
- when run:
    - creates a temporary file in /tmp with tikzpicture template
    - opens the temporary file in default editor
    - renders the file
    - on return:
        - produce an svg by compiling then using the following command: `dvisvgm -P <f>.pdf -o <f>.svg` where `<f>` is the filename.
        - copy the svg and the .tex file to the current (or output) directory
- the default filename will be 'a' (similar to the a.out from C compilation)
- 

## Options

- `[file]`           | take a previous latex image file and process it
- `-o` or `--output` | output location
- `-t` or `--type`   | an alternate type (pdf_latex or something else) 

## Template
```latex
\documentclass[tikz,border=10pt]{standalone}
\usetikzlibrary{shapes.geometric, arrows, graphs, arrows.meta,decorations.pathmorphing,backgrounds,positioning,fit,petri}

\begin{document}
\begin{tikzpicture}
% Here
\end{tikzpicture}
\end{document}
```

