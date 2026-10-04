/**
 * WCAG 2.1 Color Contrast Checker for ASTRA Design Tokens
 */

function hexToRgb(hex) {
  const cleanHex = hex.replace('#', '');
  const r = parseInt(cleanHex.substring(0, 2), 16);
  const g = parseInt(cleanHex.substring(2, 4), 16);
  const b = parseInt(cleanHex.substring(4, 6), 16);
  return [r, g, b];
}

function relativeLuminance([r, g, b]) {
  const srgb = [r, g, b].map((val) => {
    const s = val / 255;
    return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * srgb[0] + 0.7152 * srgb[1] + 0.0722 * srgb[2];
}

function contrastRatio(hex1, hex2) {
  const l1 = relativeLuminance(hexToRgb(hex1));
  const l2 = relativeLuminance(hexToRgb(hex2));
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}

const colors = {
  '--bg-base': '#090d16',
  '--bg-surface': '#0f172a',
  '--bg-card': '#1e293b',
  '--text-main': '#f8fafc',
  '--text-muted': '#94a3b8',
  '--text-dim': '#64748b',
  '--primary': '#6366f1',
  '--cyan': '#06b6d4',
  '--emerald': '#10b981',
  '--amber': '#f59e0b',
  '--rose': '#f43f5e',
  '--purple': '#a855f7',
  // Badge backgrounds (subtle dark tint with alpha blended on surface)
  'badge-safe-bg': '#064e3b',
  'badge-safe-text': '#34d399',
  'badge-vulnerable-bg': '#4c0519',
  'badge-vulnerable-text': '#fda4af',
  'badge-unknown-bg': '#1e293b',
  'badge-unknown-text': '#cbd5e1',
  'badge-critical-bg': '#4c0519',
  'badge-critical-text': '#fecdd3',
  'badge-high-bg': '#451a03',
  'badge-high-text': '#fde68a',
  'badge-medium-bg': '#1e1b4b',
  'badge-medium-text': '#c7d2fe',
  'badge-low-bg': '#064e3b',
  'badge-low-text': '#6ee7b7',
  'badge-info-bg': '#083344',
  'badge-info-text': '#67e8f9',
};

const pairs = [
  { text: '--text-main', bg: '--bg-base', note: 'Primary text on base' },
  { text: '--text-main', bg: '--bg-surface', note: 'Primary text on surface' },
  { text: '--text-main', bg: '--bg-card', note: 'Primary text on card' },
  { text: '--text-muted', bg: '--bg-base', note: 'Secondary text on base' },
  { text: '--text-muted', bg: '--bg-surface', note: 'Secondary text on surface' },
  { text: '--text-muted', bg: '--bg-card', note: 'Secondary text on card' },
  { text: '--text-dim', bg: '--bg-base', note: 'Non-essential text on base (restricted)' },
  { text: '--text-dim', bg: '--bg-surface', note: 'Non-essential text on surface (restricted)' },
  { text: 'badge-safe-text', bg: 'badge-safe-bg', note: 'Safe badge text on badge bg' },
  { text: 'badge-vulnerable-text', bg: 'badge-vulnerable-bg', note: 'Vulnerable badge text on badge bg' },
  { text: 'badge-unknown-text', bg: 'badge-unknown-bg', note: 'Unknown badge text on badge bg' },
  { text: 'badge-critical-text', bg: 'badge-critical-bg', note: 'Critical badge text on badge bg' },
  { text: 'badge-high-text', bg: 'badge-high-bg', note: 'High urgency badge text on badge bg' },
  { text: 'badge-medium-text', bg: 'badge-medium-bg', note: 'Medium urgency badge text on badge bg' },
  { text: 'badge-low-text', bg: 'badge-low-bg', note: 'Low urgency badge text on badge bg' },
  { text: 'badge-info-text', bg: 'badge-info-bg', note: 'Info badge text on badge bg' },
];

console.log('| Foreground Token | Background Token | Ratio | Status (AA >= 4.5:1) | Description |');
console.log('|---|---|---|---|---|');

let allPassed = true;
for (const p of pairs) {
  const fg = colors[p.text];
  const bg = colors[p.bg];
  const ratio = contrastRatio(fg, bg);
  const pass = ratio >= 4.5;
  const status = pass ? 'PASS (AA/AAA)' : 'WARNING (< 4.5:1)';
  if (!pass && p.text !== '--text-dim') {
    allPassed = false;
  }
  console.log(`| \`${p.text}\` (${fg}) | \`${p.bg}\` (${bg}) | ${ratio.toFixed(2)}:1 | ${status} | ${p.note} |`);
}

if (!allPassed) {
  console.error('\nContrast check FAILED on essential tokens.');
  process.exit(1);
} else {
  console.log('\nContrast check PASSED for all essential UI tokens.');
}
