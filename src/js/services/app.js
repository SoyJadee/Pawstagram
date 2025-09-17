import { initializeSupabase } from './supabase.js';

export async function initializeApp() {
    // Initialize Supabase
    initializeSupabase();
    
    // Initialize other services
    console.log('App services initialized');
    
    return true;
}