# Normalization transducers

Four `pyformlang.fst.FST` machines are built, one per category. The catalog defines equivalences; actual translation uses `translate(list(raw.casefold()))`, not a dictionary lookup returning symbols.

## Complete septuple

For category C, M_C = (Q_C, Σ_C, Γ_C, δ_C, ω_C, q0, F_C). Let i be the catalog skill index, j the alias index, a_ij = casefold(alias_ij), n_ij its length and c_i its canonical symbol. Include only skills in C.

- Q_C = {q0} ∪ {s{i}_a{j}_{k} : category(i)=C, 0≤j<len(aliases_i), 1≤k≤n_ij}. i,j are zero-based; k starts at one.
- Σ_C = {a_ij[k−1] : category(i)=C, 1≤k≤n_ij}. Letters, punctuation, spaces and accents are individual symbols.
- Γ_C = {c_i : category(i)=C}; JAVASCRIPT is one complete output symbol.
- δ_C ⊆ Q_C × Σ_C × Q_C is a transition relation. It contains (q0, a_ij[0], s{i}_a{j}_1) and (s{i}_a{j}_{k−1}, a_ij[k−1], s{i}_a{j}_{k}) for 2≤k≤n_ij.
- ω_C: δ_C → Γ_C* is the output function. It assigns ε when k<n_ij and the one-symbol word [c_i] when k=n_ij. It is defined on (source,input,target), because an input character may have multiple targets from q0.
- q0 is the sole initial state and is not final.
- F_C = {s{i}_a{j}_{n_ij} : category(i)=C}. Acceptance consumes the complete input and ends in F_C.

There are no other transitions. Alias paths are disjoint except q0. Shared first characters introduce nondeterminism; there are no epsilon-input transitions. Empty output still consumes an input character. The construction is not claimed to be minimal.

The machine accepts an input only after consuming every character and reaching a final state. Concatenating the outputs of that accepting run produces one canonical symbol. Catalog validation prevents a complete casefolded alias from belonging to two skills, so nondeterministic branching does not introduce conflicting canonical translations.

`casefold()` is a separate preprocessor applied to a copy of the raw alias. It is not a transition of the FST and does not collapse punctuation, separators or repeated internal spaces. The original resume text and its evidence offsets remain unchanged.

## Machines and complete exports

| Category | States | Transitions | Finals | Γ |
|---|---:|---:|---:|---|
| languages | 78 | 77 | 11 | JAVA, JAVASCRIPT, PYTHON, TYPESCRIPT |
| frameworks_libraries | 166 | 165 | 22 | ANGULAR, DJANGO, NODE_JS, NUMPY, PANDAS, PYTORCH, REACT, SCIKIT_LEARN, SPRING_BOOT, TENSORFLOW, VUE |
| databases | 67 | 66 | 7 | MONGODB, MYSQL, POSTGRESQL, SQL |
| tools_qualifications | 207 | 206 | 16 | AIRFLOW, APACHE_SPARK, DOCKER, ETL, GIT, ML_MODEL, REST_API |

Each JSON lists Q, Sigma, Gamma, delta, omega, q0 and F. SVGs show every state/path; open in a browser and zoom. `␠` means space; double circles mark final states; output symbols appear below the last edge.

| Machine | Complete septuple and relations | Diagram |
|---|---|---|
| Languages | [JSON](models/languages.json) | [SVG](models/languages.svg) |
| Frameworks/libraries | [JSON](models/frameworks_libraries.json) | [SVG](models/frameworks_libraries.svg) |
| Databases | [JSON](models/databases.json) | [SVG](models/databases.svg) |
| Tools/qualifications | [JSON](models/tools_qualifications.json) | [SVG](models/tools_qualifications.svg) |

## Explained paths

[Worked paths with compact SVGs, Mermaid diagrams and transition tables](models/examples/README.md) show `JS`, `React.js`, `Postgres` and `Git SCM`. Each is an alias-path subset of its full category machine, using real state names and labels. Omitted branches remain in the production machine; these views do not claim that it is deterministic or minimized. Regenerate with `python tools/export_model_examples.py`, then use `--check` to verify the stored views.

`JS` becomes `js`: q0 reads j, reaches s0_a1_1 and emits ε; s reaches s0_a1_2 and emits JAVASCRIPT. Input is exhausted and the state is final. JSx has no transition for x.

| Step | Source | Input | Target | Output |
|---:|---|---|---|---|
| 1 | q0 | j | s0_a1_1 | ε |
| 2 | s0_a1_1 | s | s0_a1_2 | JAVASCRIPT |

The transition labels read `input / output`. The first edge consumes `j` despite writing nothing; the second writes the complete one-symbol output `JAVASCRIPT`. Its letters are not separate output symbols.

`React.js` follows q0 → s4_a1_1 → … → s4_a1_8, reading r,e,a,c,t,.,j,s. The first seven edges emit ε and the last emits REACT. The dot is literal; ReactXjs has no such path.

`Postgres` follows q0 → s11_a1_1 → … → s11_a1_8, consuming p,o,s,t,g,r,e,s and emitting POSTGRESQL on the final edge. SQL is not added; POSTGRESQL is a separate profile-pattern alternative.

`Git SCM` follows q0 → s20_a1_1 → … → s20_a1_7, reading g,i,t,space,s,c,m and emitting GIT at the end. Internal space is exact: Git  SCM is not a complete FST alias, although extraction may match the shorter Git mention.

## Additional transformations and limits

Structured Query Language → SQL, Type Script → TYPESCRIPT, Git SCM → GIT and the Spanish alias `extracción transformación carga` → ETL extend the assignment examples. Its English alias `extract transform load` also maps to ETL. Docker Desktop is abstracted to DOCKER; ML_MODEL denotes a model mention without proving development. PySpark does not imply Apache Spark.

`casefold()` prepares a copy without removing accents or normalizing internal spaces/combining Unicode. Unknown input cannot reach a final and is recorded if passed to normalization. Conflicting casefolded aliases are rejected before machine construction.

`python tools/export_models.py` regenerates exports from executable machines. Graphviz is unnecessary: the tool produces direct SVG and standard DOT. Foundations: [official API](https://pyformlang.readthedocs.io/en/latest/modules/fst.html) and [Mohri 1997](https://aclanthology.org/J97-2003/); catalog and construction are project design decisions.
