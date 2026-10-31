/**
 * Display-only projections for the existing Desktop Commander file preview.
 * The tool payload, raw copy action and filesystem line coordinates stay intact.
 */
const dcPacketStates = new WeakMap();
const DC_PACKET_INPUT_LIMIT = 1024 * 1024;
const DC_PACKET_OUTPUT_LIMIT = 1024 * 1024;
const DC_PACKET_DISPLAY_LIMIT = 48 * 1024;
const DC_PACKET_DISPLAY_LINES = 240;

export function dcIsPacket(payload) {
    return payload?.fileType === 'unsupported'
        && /\.packet$/i.test(payload.filePath ?? '');
}

export function dcParentLabel(filePath) {
    const normalized = filePath.replace(/\\/g, '/');
    const separator = normalized.lastIndexOf('/');
    return separator < 0 ? '.' : normalized.slice(0, separator).split('/').filter(Boolean).pop() || '/';
}

export function dcDisablePacketSelection(previous, clearContext) {
    if (previous) {
        previous.abort();
        clearContext?.('');
    }
    return null;
}

function dcExcerpt(source) {
    const prefix = source.slice(0, DC_PACKET_DISPLAY_LIMIT);
    const lines = prefix.split('\n');
    const content = lines.slice(0, DC_PACKET_DISPLAY_LINES).join('\n');
    return { content, truncated: content.length < source.length };
}

function dcCheckJsonComplexity(value) {
    const pending = [[value, 0]];
    let remaining = 20000;
    while (pending.length) {
        const [item, depth] = pending.pop();
        if (--remaining < 0 || depth > 32) {
            throw new Error('complexity');
        }
        if (item !== null && typeof item === 'object') {
            const children = Object.values(item);
            if (children.length > remaining) {
                throw new Error('complexity');
            }
            for (const child of children) pending.push([child, depth + 1]);
        }
    }
}

export function dcPreparePacketPreview(payload, source, range, onReady) {
    if (!dcIsPacket(payload) || dcPacketStates.has(payload)) return;
    const state = { status: 'pending', original: dcExcerpt(source) };
    dcPacketStates.set(payload, state);
    const original = (reason) => {
        state.status = 'original';
        state.reason = reason;
    };
    if (range?.isPartial) {
        original('Partial read · original source');
        return;
    }
    if (source.length > DC_PACKET_INPUT_LIMIT) {
        original('Preview too large · original source');
        return;
    }
    if (typeof DecompressionStream !== 'function') {
        original('Gzip preview unavailable · original source');
        return;
    }
    void (async () => {
        let reader;
        try {
            const encoded = source.replace(/\s+/g, '');
            if (!encoded || encoded.length % 4 !== 0
                || !/^[A-Za-z0-9+/]*={0,2}$/.test(encoded)) {
                throw new Error('format');
            }
            const binary = atob(encoded);
            const bytes = Uint8Array.from(binary, (character) => character.charCodeAt(0));
            if (bytes[0] !== 0x1f || bytes[1] !== 0x8b) throw new Error('format');
            reader = new Blob([bytes]).stream()
                .pipeThrough(new DecompressionStream('gzip')).getReader();
            const chunks = [];
            let total = 0;
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                total += value.byteLength;
                if (total > DC_PACKET_OUTPUT_LIMIT) {
                    await reader.cancel();
                    original('Preview too large · original source');
                    return;
                }
                chunks.push(value);
            }
            const decoded = new Uint8Array(total);
            let offset = 0;
            for (const chunk of chunks) {
                decoded.set(chunk, offset);
                offset += chunk.byteLength;
            }
            const value = JSON.parse(new TextDecoder('utf-8', { fatal: true }).decode(decoded));
            dcCheckJsonComplexity(value);
            state.preview = dcExcerpt(JSON.stringify(value, null, 2));
            state.status = 'decoded';
        } catch {
            original('Preview unavailable · original source');
        } finally {
            reader?.releaseLock();
            onReady?.();
        }
    })();
}

export function dcPacketPreviewBody(payload, renderRawFallback) {
    if (!dcIsPacket(payload)) return undefined;
    const state = dcPacketStates.get(payload);
    if (!state || state.status === 'pending') {
        return {
            notice: 'Preparing preview…',
            html: '<div class="panel-content source-content packet-preview"></div>',
        };
    }
    const excerpt = state.status === 'decoded' ? state.preview : state.original;
    const suffix = excerpt.truncated ? ' · excerpt' : '';
    const notice = state.status === 'decoded'
        ? 'Decoded JSON preview'
        : state.reason;
    return {
        notice: notice + suffix,
        html: '<div class="panel-content source-content packet-preview">' + renderRawFallback(excerpt.content) + '</div>',
    };
}

export function dcPacketFooter(payload, fallback) {
    return dcIsPacket(payload) ? 'PACKET' : fallback;
}

export function dcCopySourceLabel(payload) {
    return dcIsPacket(payload) ? 'Copy original encoded source' : 'Copy source';
}
