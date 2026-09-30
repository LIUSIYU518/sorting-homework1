"""Generate the report and charts from recorded results; does not rerun timing."""
import argparse
import csv
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, Preformatted
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import reportlab
font_dir = Path(reportlab.__file__).parent / "fonts"
pdfmetrics.registerFont(TTFont("Vera", str(font_dir / "Vera.ttf")))
pdfmetrics.registerFont(TTFont("Vera-Bold", str(font_dir / "VeraBd.ttf")))
pdfmetrics.registerFont(TTFont("Vera-Italic", str(font_dir / "VeraIt.ttf")))
pdfmetrics.registerFont(TTFont("Vera-BoldItalic", str(font_dir / "VeraBI.ttf")))
pdfmetrics.registerFontFamily("Vera", normal="Vera", bold="Vera-Bold", italic="Vera-Italic", boldItalic="Vera-BoldItalic")

p = argparse.ArgumentParser()
p.add_argument('--repo-url', default='')
p.add_argument('--student-id', default='')
args = p.parse_args()
rows = list(csv.DictReader(open('results/summary.csv')))
env = json.loads(Path('results/environment.json').read_text())
verification = json.loads(Path('results/verification.json').read_text())
demo = json.loads(Path('results/demo.json').read_text())
Path('report').mkdir(exist_ok=True)
patterns = ['Random', 'Sorted', 'Reverse', 'Duplicates']
algorithms = ['Insertion', 'Bubble', 'Heap']
N = max(env['sizes'])

def row(n, pattern, name):
    return next(r for r in rows if int(r['n']) == n and r['pattern'] == pattern and r['algorithm'] == name)

for metric, filename, ylabel in [('median_ms', 'timing.png', 'Median sorting time (ms)'),
                                 ('mean_comparisons', 'comparisons.png', 'Mean key comparisons')]:
    fig, axes = plt.subplots(2, 2, figsize=(9, 5.4))
    for ax, pattern in zip(axes.flat, patterns):
        for name in algorithms:
            ax.plot(env['sizes'], [float(row(n, pattern, name)[metric]) for n in env['sizes']],
                    marker='o', markersize=3, label=name)
        ax.set_title(pattern); ax.set_xlabel('Input size n'); ax.set_ylabel(ylabel)
        ax.grid(alpha=.25); ax.set_ylim(bottom=0)
    axes[0, 0].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig('report/' + filename, dpi=180)
    plt.close(fig)

styles = getSampleStyleSheet()
for style in styles.byName.values():
    style.fontName = 'Vera-Bold' if style.name.startswith('Heading') else 'Vera'
styles.add(ParagraphStyle(name='BodyCustom', fontName='Vera', fontSize=9.5, leading=13.5, spaceAfter=8))
styles.add(ParagraphStyle(name='SmallCustom', fontName='Vera', fontSize=8.1, leading=11, spaceAfter=6))
styles['Title'].fontSize=23; styles['Title'].leading=28
styles['Heading1'].textColor=colors.HexColor('#123b63')
styles['Heading1'].fontSize=17
styles['Heading2'].fontSize=12; styles['Heading2'].textColor=colors.HexColor('#123b63')
story=[]; md=[]
def title(t):
    story.append(Paragraph(t, styles['Heading1'])); md.append('# '+t+'\n')
def sub(t):
    story.append(Paragraph(t, styles['Heading2'])); md.append('## '+t+'\n')
def body(t, small=False):
    story.append(Paragraph(t, styles['SmallCustom' if small else 'BodyCustom'])); md.append(t.replace('<b>','').replace('</b>','').replace('<br/>','\n')+'\n')
def table(data, widths=None):
    wrapped=[[Paragraph(str(x), styles['SmallCustom']) for x in r] for r in data]
    t=Table(wrapped, colWidths=widths, repeatRows=1, hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e5eef6')),
        ('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.6,colors.HexColor('#7890a5')),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f5f7fa')]),
        ('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
    story.extend([t,Spacer(1,10)])
    md.append('\n'.join('| '+' | '.join(map(str,r))+' |' for r in [data[0],['---']*len(data[0])]+data[1:])+'\n')
def page(): story.append(PageBreak())

title('Homework 1: Compare Sorting')
body('<b>Insertion Sort, Bubble Sort and Heap Sort</b>')
body('Advanced Algorithms | Yonsei University | 30 September 2026')
body('Student: LIU, SIYU')
body('Student ID: '+args.student_id)
body('GitHub repository URL: '+args.repo_url)
body('The student ID and repository URL can also be entered in the editable fields at the bottom of this page.', True)
sub('1. Code report')
sub('1.1 Choice of algorithms')
body('For this assignment, I chose Insertion Sort and Bubble Sort from the algorithms covered in class, and Heap Sort as the new algorithm. The comparison uses the same input for all three. I wanted to compare their running times and see how the results change when the input is already sorted, reversed or contains many repeated values.')
body('Heap Sort was chosen from the Wikipedia list because its worst-case time is O(n log n), while Insertion Sort and Bubble Sort can take O(n squared). This makes the difference easier to see as the input gets larger. The code sorts the items directly instead of calling Python sorted() or list.sort().')
sub('1.2 File structure and interface')
table([['File','Purpose'],['sorting.py','Three sorting functions, sift_down and optional counters.'],['verify.py / demo.py','Correctness checks, stability test and small number example.'],['benchmark.py','Paired-input experiment; raw data, summaries and environment.'],['build_report.py','Charts and PDF generated from the saved results.'],['results/','CSV data and JSON verification / environment records.']], [130,385])
body('The three sorting functions have the same inputs: a list, a key function and an optional counter. They change the original list and return no value. For normal numbers, the number itself is compared. For the stability test, only the first part of each (key, tag) pair is compared. Using the same interface makes the experiments easier to run.', True)
sub('1.3 Design choices and checks')
body('The experiment calls all algorithms through the same ALGORITHMS dictionary. This keeps the input copying, timer and checking method the same. A key function makes it possible to sort both numbers and records. Passing stats=None turns off the counters during timing. The common helpers greater() and swap() keep the counting rules consistent.', True)
story.append(Preformatted('insertion_sort(a, key=identity, stats=None)\nbubble_sort(a, key=identity, stats=None)\nheap_sort(a, key=identity, stats=None)', styles['SmallCustom']))
body('Run python3 verify.py to check correctness and stability, and python3 demo.py to reproduce the small numerical example. Run python3 benchmark.py for the full experiment. The sorting and testing code needs only the Python standard library.', True)
page()

title('2. Algorithm report')
sub('2.1 Insertion Sort')
body('Insertion Sort keeps the left part of the list sorted. It takes the next value, moves larger values to the right, and puts the saved value into the correct place. The sorted part grows by one item each time. Equal values are not moved past each other, so the algorithm is stable.')
body('For example, [4, 2, 3] becomes [2, 4, 3] after inserting 2, and then [2, 3, 4] after inserting 3. If the list is already sorted, only n - 1 comparisons are needed. With distinct values in reverse order, the number is 1 + 2 + ... + (n - 1) = n(n - 1)/2. Its best time is O(n), and its average and worst time are O(n squared).')
sub('2.2 Bubble Sort')
body('Bubble Sort compares two neighboring values and swaps them if the left one is larger. After one pass, the largest remaining value is at the end, so the next pass can be shorter. In this code, the loop stops early if a complete pass has no swaps.')
body('For [4, 2, 3], the first pass changes the list to [2, 4, 3] and then [2, 3, 4]. The next pass has no swaps and stops. Because of this early-stop condition, sorted input takes O(n) time. Average and worst time are O(n squared). Equal neighboring values are not swapped, so their original order is kept.')
sub('2.3 Heap Sort: self-study algorithm')
body('Heap Sort uses a max-heap. This means each parent is at least as large as its children, and the largest value is at the root. The tree is stored in the original list. If a node is at index i, its children are at 2i + 1 and 2i + 2.')
body('There are two main steps. First, build the heap by calling sift_down from the last parent back to the root. Second, swap the root with the last item in the heap. That largest value is now in its final position. Reduce the heap size and use sift_down again to repair it. Repeating this puts all values in ascending order.')
body('Building the heap from the bottom takes O(n) time because most nodes are near the leaves and need little work. Each later repair follows a path of at most O(log n) levels. There are n - 1 extractions, so the total worst-case time is O(n log n). This code uses loops instead of recursion and needs O(1) extra space. It is not stable because a swap can move one equal-key item past another.')
table([['Algorithm','Best time','Average / worst','Extra space','Stable?'],['Insertion','O(n)','O(n squared)','O(1)','Yes'],['Bubble*','O(n)','O(n squared)','O(1)','Yes'],['Heap','O(n log n)**','O(n log n)','O(1)','No']], [85,110,145,85,90])
body('* Bubble Sort includes early stopping. ** Heap best case shown for distinct keys; all equal keys take O(n) in this code. Average time assumes random ordering of distinct keys.', True)
page()

title('2.4 Numerical example and Heap Sort flow')
body('The instructor uses the list [5, 1, 4, 2] to explain Bubble Sort. The same list is used here to show all three algorithms. These steps can be checked using demo.py. In the assignment trace, a swap appears as two writes, so an intermediate trace entry can temporarily contain a repeated value.')
table([['Algorithm', 'Main states'],
    ['Insertion', '[5, 1, 4, 2] -> [1, 5, 4, 2] -> [1, 4, 5, 2] -> [1, 2, 4, 5]'],
    ['Bubble', '[5, 1, 4, 2] -> [1, 5, 4, 2] -> [1, 4, 5, 2] -> [1, 4, 2, 5] -> [1, 2, 4, 5]'],
    ['Heap', 'Build: [5, 2, 4, 1]. After extracting and repairing: [4, 2, 1, 5] -> [2, 1, 4, 5] -> [1, 2, 4, 5].']], [85,430])
table([['Algorithm','Key comparisons','Array writes'],
    *[[name,demo['algorithms'][name]['comparisons'],demo['algorithms'][name]['writes']] for name in algorithms]], [135,190,190])
body('All three sorts use six key comparisons for this example, but the number of writes differs. Insertion shifts values, while Bubble and Heap exchange pairs. In this Python code, a swap counts as two array writes. The instructor counts three moves for a C swap, including the temporary-variable assignment. These are different counting rules, so the movement numbers should not be compared directly.', True)
# Draw a branching / looping flow, not a screenshot from the instructor.
fig, ax = plt.subplots(figsize=(8, 3.6))
ax.set_xlim(0,10); ax.set_ylim(0,5); ax.axis('off')
def box(x,y,t):
    ax.text(x,y,t,ha='center',va='center',fontsize=9,bbox=dict(boxstyle='round,pad=.55',fc='#e5eef6',ec='#50789b'))
def arrow(a,b,label=None):
    ax.annotate('',xy=b,xytext=a,arrowprops=dict(arrowstyle='->',color='#50789b'))
    if label: ax.text((a[0]+b[0])/2,(a[1]+b[1])/2+.12,label,fontsize=8,ha='center')
box(2,4.3,'Build max-heap'); box(2,2.8,'Heap size > 1?'); box(7,2.8,'Swap root with last item\nReduce heap size by one'); box(7,1.1,'Sift down the new root'); box(2,1.1,'Finished: ascending order')
arrow((2,3.95),(2,3.18));arrow((2.95,2.8),(5.6,2.8),'Yes');arrow((2,2.4),(2,1.48),'No');arrow((7,2.3),(7,1.55))
ax.plot([8.5,9.4,9.4,2],[1.1,1.1,3.6,3.6],color='#50789b',linewidth=1)
arrow((2,3.6),(2,3.18))
ax.text(9.1,3.85,'Repeat',fontsize=8,ha='center')
fig.tight_layout(); fig.savefig('report/heap_flow.png',dpi=170);plt.close(fig)
story.append(Image('report/heap_flow.png',width=480,height=216));md.append('![Heap Sort flow](heap_flow.png)\n')
body('Before each extraction, the active part is a max-heap. The last part is already sorted. Moving the maximum to the last active position grows the sorted part by one item.', True)
page()

title('3. Algorithm experiments')
sub('3.1 Input data')
body(f"Input sizes are {', '.join(map(str,env['sizes']))}. Each size and pattern has {env['repeats']} trials. Base seed is {env['seed']}. Every algorithm receives a fresh copy of the same array in a trial. Algorithm order is shuffled with a seeded generator. Random and duplicate-heavy arrays vary between trials; sorted and reverse arrays repeat the same deterministic input.")
table([['Pattern','Construction'],['Random','Uniform integer draws from 0 through 10n - 1.'],['Sorted','Distinct integers 0 through n - 1 in ascending order.'],['Reverse','The same distinct integers in descending order.'],['Duplicates','Uniform integer draws from 0 through 9.']], [100,415])
sub('3.2 Measurements')
body('The program measures sorting time with perf_counter_ns. The report uses the median of five runs, in milliseconds. Creating and copying the input, checking the answer and saving files are not included in the time. Each algorithm has a small warm-up run first. Comparisons and writes are counted in separate runs, so the counters do not affect the reported time.')
body('A comparison is one comparison between two keys, even when the condition is false. Loop and index checks are not counted. A write is one assignment to a list position, so a swap counts as two writes. Memory is checked separately with tracemalloc at the largest input size, once for each algorithm and input type. Tracing starts after the input copy is made, so the values show extra Python allocation during sorting, not the total memory of the program.')
sub('3.3 Correctness and stability')
body(f"Validation uses {verification['input_cases']:,} integer input cases, including every array of length 0 to 6 over [-1, 0, 1] and 100 seeded random arrays. Counted and uncounted versions are both checked, for {verification['integer_correctness_checks']:,} checks in total. Each result must exactly match Python sorted(source), checking both order and element preservation. Python sorted() is used only to check the results, not inside the three sorting functions.")
body('For stability, use (key, tag) records and compare only the key. Input: (2,A), (1,B), (2,C), (1,D), (2,E). Insertion and Bubble output (1,B), (1,D), (2,A), (2,C), (2,E). Heap outputs (1,B), (1,D), (2,C), (2,E), (2,A), reversing the order of some equal-key records. Insertion and Bubble also pass tagged-record checks across all integer test cases.')
sub('3.4 Execution environment')
body(f"Python {env['python']}; {env['platform']}. These results were generated in Codex's Linux environment with AI assistance, rather than on my own computer. Processor identifier: {env['processor']}; detailed CPU model was not exposed. Results should be rerun locally when comparing absolute speed.",True)
page()

title('3.5 Results: running time')
body('The experiment contains 300 timed runs. Every output matched the expected sorted list. The following graphs and table show the times recorded by the program.')
story.append(Image('report/timing.png',width=515,height=309)); md.append('![Timing](timing.png)\n')
sub(f'Timing at n = {N:,}')
data=[['Input','Insertion (ms)','Bubble (ms)','Heap (ms)']]
for pat in patterns:
    data.append([pat]+[f"{float(row(N,pat,a)['median_ms']):.3f}" for a in algorithms])
table(data,[110,135,135,135])
rand=[float(row(N,'Random',a)['median_ms']) for a in algorithms]
body(f'At n = {N:,}, Heap Sort is {rand[0]/rand[2]:.1f} times faster than Insertion Sort and {rand[1]/rand[2]:.1f} times faster than Bubble Sort on the random inputs in this run. The random and reverse curves show a much stronger size effect for the quadratic algorithms. Sorted input is different: Insertion and Bubble need only one linear scan, while Heap still reorganizes the distinct keys.')
body('With many repeated values, the algorithms do not swap or shift equal values. This helps explain why the results differ from the random-input case. Here, the repeated values are limited to the integers 0 through 9.',True)
page()

title('3.6 Results: comparisons and writes')
story.append(Image('report/comparisons.png',width=470,height=282));md.append('![Comparisons](comparisons.png)\n')
sub(f'Mean operations at n = {N:,}')
data=[['Input','Algorithm','Key comparisons','Array writes']]
for pat in patterns:
    for a in algorithms:
        r=row(N,pat,a)
        data.append([pat,a,f"{float(r['mean_comparisons']):,.1f}",f"{float(r['mean_writes']):,.1f}"])
table(data,[105,100,155,155])
body(f'For distinct reverse input, n(n - 1)/2 = {N*(N-1)//2:,}, matching the comparison counts of Insertion and Bubble. Bubble writes twice per swap; Insertion shifts and then places each saved item. This shows why two algorithms with similar comparison counts can still take different amounts of time.',True)
page()

title('3.7 What happens when n doubles?')
body('The instructor compares increasing sizes to check how quickly the work grows. The table below uses our random-input results at n = 500, 1,000 and 2,000. Each entry is the mean comparison count over five trials. The ratio is the count divided by the count at the previous size.')
data=[['n','Insertion / ratio','Bubble / ratio','Heap / ratio']]
previous={}
for n in [500,1000,2000]:
    entries=[]
    for name in algorithms:
        count=float(row(n,'Random',name)['mean_comparisons'])
        ratio='-' if name not in previous else f'{count/previous[name]:.2f}x'
        entries.append(f'{count:,.1f} / {ratio}');previous[name]=count
    data.append([n]+entries)
table(data,[45,157,157,156])
body('For the two quadratic algorithms, doubling n makes the comparison count close to four times as large: (2n) squared = 4n squared. Heap Sort grows more slowly. For n log n, doubling n gives a ratio of 2 log(2n) / log(n), a little above two. Finite measurements support this pattern but do not prove the complexity bound.')
sub('Array writes by input type')
fig, ax=plt.subplots(figsize=(8.5,3.5))
for ai,name in enumerate(algorithms):
    positions=[i+(ai-1)*.24 for i in range(4)]
    bars=ax.bar(positions,[float(row(N,pat,name)['mean_writes']) for pat in patterns],width=.24,label=name)
    ax.bar_label(bars,labels=[f'{float(row(N,pat,name)["mean_writes"]):,.0f}' for pat in patterns],fontsize=7,padding=3,rotation=30)
ax.set_xticks(range(4),patterns);ax.set_ylabel('Mean array writes');ax.set_title(f'n = {N:,}, five trials');ax.legend(fontsize=8);ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True);ax.set_ylim(0,ax.get_ylim()[1]*1.25)
fig.tight_layout();fig.savefig('report/writes.png',dpi=180);plt.close(fig)
story.append(Image('report/writes.png',width=500,height=206));md.append('![Array writes](writes.png)\n')
body('Bubble Sort makes many writes on reverse input because every comparison causes a swap. Insertion Sort shifts one value at a time and writes fewer array positions. On sorted input, Bubble makes no writes, but this Insertion implementation still places each saved value back into its position. That counts as n - 1 writes even when the list does not change.')
sub('Recursion and counting conventions')
body('These three implementations use loops, including sift_down. Their recursive depth is zero. Heap Sort calls a helper, but it does not call itself recursively. The experiment reports Python allocation separately rather than copying the C sample\'s eight-byte memory figure. The language, input generator and counting rules differ from the instructor\'s example.', True)
page()

title('3.8 Memory, discussion and AI learning')
sub('Extra memory')
data=[['Input','Insertion peak (B)','Bubble peak (B)','Heap peak (B)']]
for pat in patterns:
    data.append([pat]+[str(next(r['peak_traced_bytes'] for r in env['memory'] if r['pattern']==pat and r['algorithm']==a)) for a in algorithms])
table(data,[110,135,135,135])
body('All three algorithms use only a few temporary variables and do not create another list inside the sort. Their extra space is O(1). The measured byte counts are slightly different because Python also allocates temporary objects. O(1) means the number of working variables stays constant; it does not mean that no extra memory is used.')
sub('AI-assisted learning: Heap Sort')
body('AI was used to explain Heap Sort and help prepare the code, experiments and report. The main learning points are listed below, as required for the algorithm not covered in class.')
body('<b>What is a heap?</b> A max-heap is a complete binary tree stored in an array, with each parent at least as large as its children. It is not a fully sorted array. Only the largest key is guaranteed to be at the root.')
body('<b>How does it sort?</b> Build the heap from the last internal node backward. Exchange the root with the last active element, reduce the active size, and repair the root by repeatedly exchanging it with its larger child. The sorted suffix grows by one position per extraction.')
body('<b>Why O(n log n)?</b> The heap height is O(log n), so a repair is at most logarithmic. There are n - 1 extractions. Bottom-up construction is O(n), because most nodes are close to the leaves and require little repair work.')
body('<b>Why is it unstable?</b> A root-to-end exchange can move an equal-key record past another one. The tagged-record test shows this behavior without comparing the tags. Iterative sift-down keeps auxiliary space constant.')
sub('Conclusion and limits')
body('The main result is that Heap Sort is faster for the larger random and reverse inputs in this experiment. However, when the input is already sorted, Insertion Sort and Bubble Sort are faster because they can finish with a simple scan. Insertion Sort and Bubble Sort also keep equal-key items in their original order, while Heap Sort does not. The choice therefore depends on both the input and whether stability is needed.')
body('This comparison uses five trials and at most 2,000 values. The exact times can change on another computer, and larger inputs may give different speed ratios. The saved CSV files include the smallest and largest times as well as the medians.',True)
sub('References')
body('[1] Wikipedia, Sorting algorithm, comparison of algorithms: https://en.wikipedia.org/wiki/Sorting_algorithm#Comparison_of_algorithms<br/>[2] Wikipedia, Heapsort: https://en.wikipedia.org/wiki/Heapsort<br/>[3] Sedgewick and Wayne, Algorithms, 4th ed., companion section 2.4 (heap construction and sortdown): https://algs4.cs.princeton.edu/24pq/<br/>Accessed 30 September 2026. Course material: Topic 03, Divide and Conquer and Merge Sort (pp. 2, 25 and 43); Homework 1 instructions and the instructor\'s sample report screenshots.',True)

# Keep submission fields editable in PDF viewers that support forms.
def decorate(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor('#d5dfe8')); canvas.line(40,38,555,38)
    canvas.setFont('Vera',8); canvas.setFillColor(colors.HexColor('#526478'))
    canvas.drawString(40,26,'Homework 1 | Compare Sorting'); canvas.drawRightString(555,26,str(doc.page))
    if doc.page==1:
        canvas.setFont('Vera',8)
        canvas.drawString(40,96,'Student ID (required):')
        canvas.acroForm.textfield(name='student_id', x=160,y=89,width=395,height=20,value=args.student_id,fontSize=10,borderWidth=.5)
        canvas.drawString(40,67,'GitHub URL (required):')
        canvas.acroForm.textfield(name='github_url',x=160,y=60,width=395,height=22,value=args.repo_url,fontSize=9,borderWidth=.5)
    canvas.restoreState()

SimpleDocTemplate('report/Sorting_Report.pdf',pagesize=(595.28,841.89),rightMargin=40,leftMargin=40,topMargin=40,bottomMargin=55, title='Homework 1: Compare Sorting', author='LIU, SIYU').build(story,onFirstPage=decorate,onLaterPages=decorate)
Path('report/REPORT.md').write_text('\n'.join(md),encoding='utf-8')
print('Report generated: report/Sorting_Report.pdf')
