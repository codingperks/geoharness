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
