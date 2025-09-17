// Initialize Supabase client
let supabase = null;

export async function initializeSupabase() {
    if (!supabase && typeof window !== 'undefined' && window.supabase) {
        const { supabaseConfig } = await import('../../config/config.js');
        supabase = window.supabase.createClient(supabaseConfig.url, supabaseConfig.anonKey);
    }
    return supabase;
}

export function getSupabaseClient() {
    if (!supabase) {
        throw new Error('Supabase client not initialized. Call initializeSupabase() first.');
    }
    return supabase;
}