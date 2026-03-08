import OpenAI from 'openai';
import { getPrecedents } from './memory.js';

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY || 'sk-mock' });

const PERSONAS = [
  { id: 'central_bank', name: 'Central Bank Watcher', focus: 'Policy signals, forward guidance, dot plot.' },
  { id: 'bond_trader', name: 'Bond Trader', focus: 'Duration risk, yield curve, credit spreads, real yields.' },
  { id: 'equity_strategist', name: 'Equity Strategist', focus: 'Sector rotation, P/E compression, earnings revision risk.' },
  { id: 'macro_hedge', name: 'Macro Hedge Fund', focus: 'Non-consensus trades, tail risk, asymmetric opportunities.' },
  { id: 'risk_manager', name: 'Risk Manager', focus: 'Portfolio stress, concentration, hedging instruments.' },
  { id: 'em_analyst', name: 'Emerging Market Analyst', focus: 'EM spillovers, capital flows, FX pressure, China.' },
];

function buildPrompt(persona, event, precedents) {
  const precText = precedents.length
    ? precedents.map((p) => `- ${p.title} → ${p.outcome_24h}`).join('\n')
    : 'No close precedent.';
  return `You are ${persona.name}. Focus: ${persona.focus}

Event: ${event.title}
${event.body ? `Details: ${event.body}` : ''}

Historical precedents:
${precText}

Respond in 1-2 sentences with: (1) your read on implications, (2) one specific evidence or data point (e.g. "per CME FedWatch" or "Aug 2023 analogue"). Format: "[Analysis]. [Evidence: source]."`;
}

function mockAnalysis(persona, event) {
  const lines = [
    `${persona.name}: ${event.title} suggests caution on duration. Evidence: historical rate cycles.`,
    `${persona.name}: Risk-off bias for EM FX. Evidence: DXY strength in similar setups.`,
  ];
  return lines[persona.id.length % 2];
}

export async function runSimulation(event, portfolioProfile = 'global_macro') {
  const precedents = getPrecedents(event);
  const results = { riskChain: [], agents: [], debater: null, consensus: {} };

  results.riskChain = [
    { order: 1, implication: event.title, assetClass: 'Rates' },
    { order: 2, implication: 'Repricing of front-end rates and FX', assetClass: 'FX' },
    { order: 3, implication: 'EM and risk assets under pressure', assetClass: 'EM' },
  ];

  const useOpenAI = process.env.OPENAI_API_KEY && !process.env.OPENAI_API_KEY.startsWith('sk-mock');

  if (useOpenAI) {
    try {
      for (const p of PERSONAS) {
        const prompt = buildPrompt(p, event, precedents);
        const comp = await openai.chat.completions.create({
          model: 'gpt-4o-mini',
          messages: [{ role: 'user', content: prompt }],
          max_tokens: 150,
        });
        const text = comp.choices?.[0]?.message?.content || '';
        results.agents.push({ id: p.id, name: p.name, analysis: text });
      }
      const debaterPrompt = `You are the Debater. Challenge the consensus. Given this event: "${event.title}". List one key risk the consensus might be missing and one historical counterexample (when consensus was wrong). 2-3 sentences.`;
      const deb = await openai.chat.completions.create({
        model: 'gpt-4o-mini',
        messages: [{ role: 'user', content: debaterPrompt }],
        max_tokens: 120,
      });
      results.debater = deb.choices?.[0]?.message?.content || 'Consensus may underestimate reversal risk.';
    } catch (e) {
      results.agents = PERSONAS.map((p) => ({ id: p.id, name: p.name, analysis: mockAnalysis(p, event) }));
      results.debater = 'Consensus may underestimate reversal risk. Oct 2022 CPI miss saw a sharp equity rally.';
    }
  } else {
    results.agents = PERSONAS.map((p) => ({ id: p.id, name: p.name, analysis: mockAnalysis(p, event) }));
    results.debater = 'Consensus may underestimate reversal risk. Oct 2022 CPI miss saw a sharp equity rally.';
  }

  results.consensus = { direction: 'cautious', conviction: 0.6 };
  return results;
}
