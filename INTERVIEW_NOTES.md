# Interview notes

Private prep notes, not project documentation.

## The 30 second version

I built an interactive dashboard tracking UK inflation, wages, unemployment and interest
rates, pulling live data from the ONS and Bank of England. It calculates metrics that
aren't published directly, like real interest rates and a simplified Taylor Rule, and it
has two AI features: one that explains recent changes, and one that answers natural
language questions about the data.

The design decision I'd highlight is that the AI never does arithmetic. Everything is
computed in Python and the model only explains finished figures.

## Why that design decision

Language models produce plausible sounding numbers rather than calculated ones. For
anything presenting itself as economic analysis, that's disqualifying. So I separated the
layers: calculations live in Python where they're transparent and testable, and the model
receives finished figures.

For the question answering, I used tool calling. The model chooses which Python function
to run, the function computes the answer from the dataset, and the model explains the
result. It never pulls a number from memory.
git ls-files | findstr .env
## Specific problems I hit and solved

**The Bank of England returned a webpage instead of data.** My first request looked
successful but saved an HTML page rather than a CSV. Turned out there are two endpoints
on their site, and the CSV export one has an underscore prefix. Before that, the request
was blocked entirely with a 403 until I set a browser-like User-Agent header.

**The ONS stacks three data frequencies in one column.** Their time series export puts
annual, quarterly and monthly figures in the same column, distinguished only by the
label format, for instance "2026", "2026 Q2" and "2026 AUG". I filtered to monthly
observations using a regex pattern on the label.

**Indicators publish at different speeds.** Unemployment lags furthest because it comes
from the Labour Force Survey, while CPI and Bank Rate are more current. I originally used
an inner join, which truncated everything back to the slowest series and made the
dashboard look two months out of date. I switched to an outer join so each indicator shows
its own latest month, with charts ending where their data does.

**The ONS rate limited me.** Re-fetching on every script run triggered a 429. I added a
local processed data cache so the app reads from a cleaned file and only re-fetches on
request. That also means the dashboard stays available if a government server is down.

**A prompt instruction wasn't reliably followed.** I asked the model to label any context
drawn from its own knowledge rather than the data. It hedged, but didn't consistently
label. I changed the prompt to require a specific output structure instead of a style
instruction, which made the behaviour reliable. Prompts influence behaviour, they don't
guarantee it.

## Judgment calls I should be able to defend

**CPI rather than CPIH.** CPIH is the ONS's lead measure, but CPI is what the Bank of
England's 2% target is set against, and it's what people mean by "inflation". Since the
project compares inflation to Bank Rate, CPI was the consistent choice.

**The Taylor Rule is simplified.** The standard formula uses an output gap. I don't have
GDP in this project, so I substituted unemployment's deviation from its dataset average as
a proxy for slack. It's labelled as simplified everywhere it appears. I'd rather be upfront
about the substitution than present it as the textbook version.

**GDP was excluded deliberately.** It's quarterly rather than monthly, and it's revised
repeatedly after first publication, which complicates a dashboard aiming at reproducibility.
The five indicators I chose tell a coherent story about household economic conditions and
the monetary policy response.

**The AI may add historical context, but must label it.** Purely data-only answers were
drier and less useful to a non-economist. Allowing context with mandatory labelling keeps
the boundary visible without making the output useless.

## If asked about using AI to build it

I used an AI assistant as a pair programmer. I'm a PPE student, not a developer, so I used
it to learn while building. The analytical decisions were mine: which indicators, how to
handle the messy ONS data, and deliberately architecting it so calculations happen in
Python rather than letting the model do arithmetic.

## What I'd do next

Exponential smoothing for trend projection, weighting recent observations more heavily
than older ones. Anomaly detection. Correlation analysis between unemployment and
inflation. Possibly GDP with an explicit revisions caveat.