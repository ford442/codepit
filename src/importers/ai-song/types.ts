export interface AISongData {
    title: string;
    author: string;
    tempo: number;
    tracks: any[]; // simplified track representation
    metadata?: Record<string, string>;
}

export interface VersionHistoryEntry {
    timestamp: string;
    sourceAI: string;
    notes?: string;
}