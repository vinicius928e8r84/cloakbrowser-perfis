import { readFileSync } from 'node:fs';
import globals from 'globals';
import tsParser from '@typescript-eslint/parser';

const ignorar = JSON.parse(readFileSync(new URL('./excecoes.json', import.meta.url), 'utf8'))
  .eslint.map(item => item.glob);

const correcao = {
  'no-undef': 'off',
  'no-unreachable': 'error',
  'no-dupe-keys': 'error',
  'no-dupe-else-if': 'error',
  'no-dupe-args': 'error',
  'no-duplicate-case': 'error',
  'no-func-assign': 'error',
  'no-self-assign': 'error',
  'no-unsafe-finally': 'error',
  'no-unsafe-negation': 'error',
  'no-cond-assign': ['error', 'except-parens'],
  'no-ex-assign': 'error',
  'no-const-assign': 'error',
  'no-import-assign': 'error',
  'no-sparse-arrays': 'error',
  'use-isnan': 'error',
  'valid-typeof': 'error',
  'no-debugger': 'error',
};

const opcoes = { noInlineConfig: true };

export default [
  { ignores: ['**/node_modules/**', ...ignorar] },
  {
    files: ['**/*.js', '**/*.jsx', '**/*.mjs'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      parserOptions: { ecmaFeatures: { jsx: true } },
      globals: { ...globals.browser, ...globals.node },
    },
    linterOptions: opcoes,
    rules: correcao,
  },
  {
    files: ['**/*.ts', '**/*.tsx', '**/*.mts'],
    languageOptions: {
      parser: tsParser,
      ecmaVersion: 'latest',
      sourceType: 'module',
      parserOptions: { ecmaFeatures: { jsx: true } },
      globals: { ...globals.browser, ...globals.node },
    },
    linterOptions: opcoes,
    rules: correcao,
  },
];
