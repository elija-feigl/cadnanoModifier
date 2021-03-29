# CadnanoModifier

A python3 script for modification of DNA Origami nano structure designed with [caDNAno](https://cadnano.readthedocs.io/en/master/#)

# Dependencies

* Python >= 3.7
  * click >= 7.0


# Usage
<pre>
Implemented with click, the script provides three different commands:
  * modify:  manipulate cadnano design files
  * merge:   merge two cadnano design files
  * fix:     fix faulty cadnano design files 
</pre>
  
all are called with:
  ```python3 cadnano_manipulator.py COMMAND```

## modify
Usage: ```cadnano_manipulator.py modify [OPTIONS] CADNANO```
<pre>
  manipulate cadnano design files for DNA Origami

  CADNANO is the name of the design file [.json]

Options:
  --shift-row INTEGER  shift helices by N rows. affected by selection
  --shift-col INTEGER  shift helices by N columns. affected by selection
  --shift-pos INTEGER  shift helices by N base positions. affected by
                       selection

  --fix-legacy         attempt to fix legacy design for version < 0.7
  --remove-skips       remove all skips. affected by selection
  --remove-loops       remove all loops. affected by selection
  --helix-subset TEXT  subset of helices selected by their number. format:
                       "[1,2,3]"

  --help               Show this message and exit.
</pre>

## merge
Usage: ```cadnano_manipulator.py merge [OPTIONS] CADNANO MERGE```
<pre>
  merge two cadnano design files for DNA Origami

  CADNANO is the name of the first design file [.json]

  MERGE is the name of the second design file [.json]

Options:
  --help  Show this message and exit.

## fix
Usage: ```cadnano_manipulator.py fix [OPTIONS] CADNANO```

  fix faulty cadnano design files for DNA Origami for: legacy cadnano (< 2.)
  json_modifier06.py

  CADNANO is the name of the design file [.json]

Options:
  --help  Show this message and exit.
</pre>