merge	merge and organize excel files without removing duplicates
merge2	merge and organize excel files + removing duplicates/ works on position graphs
merge3	merge and organize excel files + rename header
run_lc_2	used to run lc5 and handles oom
batch_generateur	execute generateur n times takes the number of nodes as parameter
polynomial_isomorphism	algorithme sur le grapheréduit 
ilf2	ilf but optimized: loops replaced by dict
lc5	 version of lc isomorphism solver with memory and time control bfr ilf return iterations
lc	 version lc isomorphism solver bfr handling ILF empty domain
lc6	current version lc isomorphism solver
ilf3	ilf optimiwed and break if empty domain +return iterations
generateur	generate positions graph and its equivalent ; takes number of nodes as parameter
merge4	Best seller: this script can be used on both pos and rows/cols and it merge excel of lines/cols and add target index glc_card and lctr having same index, takes results file as parameter and class file of generated graph lines/cols
analysis2 	plot a bar chart of average of effs for each pattern with/without ILF or for each target
average_class_nodes	plot two curves showing average of lines/cols graph nodes in function of pos graph nodes
analysis4	save excel file that analyses results and find percentage of oom for each filter conditions
analysis5	uexcel file of merged results of lines/cols graphs 
analysis	"plot a bar chart of average of effs for each pattern with/without ILF, save excel file that analyses results and find percentage of oom for each filter conditions, uexcel file of results of lines/cols graphs with results on pos graphs
"
disip1	"solve isomorphism in position graph , used in experiences
"
disip	solve isomorphism in position graph , print solutions not used in experiences
components_divider.py	divides a graph into its weakly connected components
verify_components.py	verify that components of a graph can reconstruct the initial graph
rows_columns_generator.	given a graph generates its rows columns graph
edges_divider.py	"parses a DOT/Graphviz file, looks at the edges, and separates them into two sets:

Edges with label ""h""

Edges with label ""v"""
components_divider_1	divides a graph into its weakly connected components and renumbered it
run_components_divider	divides a list of pos graph into sbcompoentns and for each gives the equivalent row_cols graph
matrix_density	measures to study distribution in a matrix of 1s elements
veify_missing_indicator	verify if results file contains all graphs files 
connectivity_sum_effs	excel file for comparing effs of parent and subcomponents graphs
polynomial_compare_time	excel file to compare time between polynomial and csp appriach
effs parent vs sub	
search100	"Searches all Excel files in a folder
✔ Looks specifically for the column header file4_nodes
✔ Checks whether any row under that column contains the value 100
✔ Prints all matching file paths"
run_disip_param	run disip with patterns/targets as parameters
generateur_card	generates graphs that respects cardinality
generateur_format_1000	generates graphs in text format
readfilememo	read txt file and create a nx graph; does not break if memory error
readfile	read txt file and create a nx graph; breaks if memory error
gp_experiences_validator.py	Takes a directory path and a pattern string, Checks whether it appears exactly 40 times&&& checks for a given targets list and a directory if all targets are present 10 times (works perfectly)
run_disip	batch to run disip with timeout and memo control
disip	version of 16012026, memo and timeout control
bimodel.py	checked on 16012026, bimodel solver implementation
analysis_pos	with without ilf compares wrgs, ilf time and effs average for a given directory
plot_charts	functions takes argument x and y and if ther is a pattern to filter according to, it works on positions graphs results (also in analysis.py)
batch_rows_cols_generator	runs row cols generator, saves the generated rows column with cardinality in separated file,not in generated files db
delete_files.py	delete graph files in lcres
grc_experiences_validator	best seller: cheks wether results of bimodel are fine and return couples of pos and rc ifnot. checks results of rows/cols andr retirns patterns and targets rows/cols
run_bimodel_ilf_param	batch to run bimodel with ilf mutated
bimodel_ilf	ilf amrap for pos graph, rows cols propagation, ilf on rc then bimodel solving
