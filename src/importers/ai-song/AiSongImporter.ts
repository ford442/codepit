import { AISongData, VersionHistoryEntry } from './types';
import fs from 'fs';
import path from 'path';

const GENERATED_DIR = path.resolve(__dirname, '../../../songs/ai-generated');

export function ensureGeneratedDir() {
  if (!fs.existsSync(GENERATED_DIR)) {
    fs.mkdirSync(GENERATED_DIR, { recursive: true });
  }
}

export function saveAISongData(data: AISongData, sourceAI: string): string {
  ensureGeneratedDir();
  const ts = new Date().toISOString().replace(/[:.]/g, '-');
  const fileName = `${data.title || 'untitled'}_${ts}.json`;
  const filePath = path.join(GENERATED_DIR, fileName);
  const historyEntry: VersionHistoryEntry = {
    timestamp: ts,
    sourceAI,
  };
  const payload = { data, history: [historyEntry] };
  fs.writeFileSync(filePath, JSON.stringify(payload, null, 2), 'utf-8');
  return filePath;
}

export function appendVersionHistory(filePath: string, sourceAI: string) {
  try {
    const content = fs.readFileSync(filePath, 'utf-8');
    const json = JSON.parse(content);
    const ts = new Date().toISOString().replace(/[:.]/g, '-');
    const entry: VersionHistoryEntry = { timestamp: ts, sourceAI };
    if (!Array.isArray(json.history)) json.history = [];
    json.history.push(entry);
    fs.writeFileSync(filePath, JSON.stringify(json, null, 2), 'utf-8');
  } catch (e) {
    console.error('Failed to append history', e);
  }
}

export function validateAISongData(data: any): boolean {
  if (!data || typeof data !== 'object') return false;
  if (typeof data.tempo !== 'number') return false;
  if (!Array.isArray(data.tracks)) return false;
  return true;
}