const LOCATION_META = {
  "Algeria, North Africa": {
    why: "Chosen as a clear GOOD baseline. Saharan irradiance is among the highest globally — a sanity check that the agent identifies a near-ideal location without hesitation.",
    caveat: null,
  },
  "Almeria, Southern Spain": {
    why: "One of Europe's largest solar farm clusters. Tests whether the agent handles moderate slope alongside strong irradiance correctly.",
    caveat: null,
  },
  "Texas, Southern US": {
    why: "Represents the US Sun Belt — a well-established solar market with flat, high-irradiance terrain. Clear GOOD case.",
    caveat: null,
  },
  "N of Truro": {
    why: "Maritime climate with persistent cloud cover (~32% reduction from clear-sky). Tests whether the agent identifies cloud cover as the key limiting factor despite adequate terrain.",
    caveat: null,
  },
  "Vermont": {
    why: "Borderline MARGINAL — 3.47 kWh/m²/day with seasonal snow cover. Tests whether the agent avoids over-weighting terrain quality when the solar resource is limited.",
    caveat: null,
  },
  "N Turkey Coast": {
    why: "Conflicting signals: reasonable Mediterranean climate but coastal terrain. Tests whether the agent synthesises multiple data sources rather than pattern-matching on climate alone.",
    caveat: null,
  },
  "Croatian Coast": {
    why: "The known failure case. At 4.3 kWh/m²/day — just below the 4.5 GOOD threshold — with otherwise excellent terrain, the agent consistently returns GOOD. A legitimate borderline case; the eval rules are not softened to match.",
    caveat: "The agent rates this GOOD. Ground truth is MARGINAL. This is accepted as a known failure on a genuine boundary case.",
  },
  "N of Krakow": {
    why: "Tests northern European MARGINAL irradiance with variable terrain — a typical mid-latitude continental case.",
    caveat: null,
  },
  "Amazon Rainforest": {
    why: "Interesting edge case: irradiance is reasonable but persistent cloud cover is high. On current tool data alone it is MARGINAL. Expected to become BAD once a land cover tool is added, since dense forest cover makes the location unsuitable regardless of irradiance.",
    caveat: "Correct verdict from tool data alone. Would be BAD with satellite/land cover data — a planned tool addition.",
  },
  "Northern Norway": {
    why: "Clear BAD case — very low winter irradiance, extreme latitude, seasonal darkness. Also exercises the COP30 terrain fallback since SRTM does not cover latitudes above 60°N.",
    caveat: null,
  },
  "N-facing Swiss Alps": {
    why: "BAD case combining steep north-facing terrain with marginal Alpine irradiance. Tests whether the agent correctly penalises aspect at high slope values.",
    caveat: null,
  },
}

async function init() {
  const results = await fetch('./data/eval_results.json').then(r => r.json())
  const list = document.getElementById('location-list')
  results.forEach(result => list.appendChild(createCard(result)))
}

function createCard(result) {
  const card = document.createElement('div')
  card.className = 'card'

  const header = document.createElement('button')
  header.className = 'card-header'
  header.innerHTML = `
    <span class="location-name">${result.name}</span>
    <span class="verdict expected">Expected: ${result.expected}</span>
    <span class="verdict actual ${result.passed ? 'pass' : 'fail'}">Got: ${result.actual}</span>
  `

  const trace = document.createElement('div')
  trace.className = 'trace'
  trace.hidden = true

  const meta = LOCATION_META[result.name]
  if (meta) {
    const metaEl = document.createElement('div')
    metaEl.className = 'location-meta'
    metaEl.innerHTML = `<p class="meta-why">${meta.why}</p>${meta.caveat ? `<p class="meta-caveat">⚠ ${meta.caveat}</p>` : ''}`
    trace.appendChild(metaEl)
  }

  trace.appendChild(renderSteps(stepsFromResult(result)))

  header.addEventListener('click', () => {
    trace.hidden = !trace.hidden
    header.classList.toggle('open', !trace.hidden)
  })

  card.appendChild(header)
  card.appendChild(trace)
  return card
}

function stepsFromResult(result) {
  if (result.steps && result.steps.length > 0) return result.steps
  return [{ type: 'output', content: result.output.output }]
}

function renderStepBody(step) {
  let parsed = null
  if (typeof step.content === 'string') {
    try { parsed = JSON.parse(step.content) } catch {}
  } else if (typeof step.content === 'object') {
    parsed = step.content
  }

  if (parsed && step.type === 'output') {
    const el = document.createElement('div')
    el.className = 'step-body step-output'
    if (parsed.verdict) {
      const badge = document.createElement('span')
      badge.className = `verdict-badge verdict-${parsed.verdict.toLowerCase()}`
      badge.textContent = parsed.verdict
      el.appendChild(badge)
    }
    if (parsed.output) {
      const text = document.createElement('p')
      text.className = 'output-reasoning'
      text.textContent = parsed.output
      el.appendChild(text)
    }
    return el
  }

  const pre = document.createElement('pre')
  pre.className = 'step-body'
  pre.textContent = parsed ? JSON.stringify(parsed, null, 2) : step.content
  return pre
}

function renderSteps(steps) {
  const container = document.createElement('div')
  container.className = 'steps'
  steps.forEach(step => {
    const el = document.createElement('div')
    el.className = 'step'
    el.dataset.type = step.type

    const label = document.createElement('div')
    label.className = 'step-label'
    label.textContent = step.type

    const prompt = document.createElement('details')
    prompt.className = 'step-prompt'
    const summary = document.createElement('summary')
    summary.textContent = 'Prompt'
    const promptBody = document.createElement('pre')
    promptBody.textContent = typeof step.prompt === 'object'
      ? JSON.stringify(step.prompt, null, 2)
      : step.prompt
    prompt.appendChild(summary)
    prompt.appendChild(promptBody)

    el.appendChild(label)
    el.appendChild(prompt)
    el.appendChild(renderStepBody(step))
    container.appendChild(el)
  })
  return container
}

init()
