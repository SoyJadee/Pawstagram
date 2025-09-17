import { getSupabaseClient } from './supabase.js';

class AuthService {
    constructor() {
        this.currentUser = null;
    }

    async signUp(email, password, petData) {
        try {
            const supabase = getSupabaseClient();
            
            const { data, error } = await supabase.auth.signUp({
                email,
                password,
            });

            if (error) throw error;

            // Create pet profile
            if (data.user) {
                await this.createProfile(data.user.id, petData);
            }

            return { success: true, user: data.user };
        } catch (error) {
            console.error('Error signing up:', error);
            return { success: false, error: error.message };
        }
    }

    async signIn(email, password) {
        try {
            const supabase = getSupabaseClient();
            
            const { data, error } = await supabase.auth.signInWithPassword({
                email,
                password,
            });

            if (error) throw error;

            this.currentUser = data.user;
            return { success: true, user: data.user };
        } catch (error) {
            console.error('Error signing in:', error);
            return { success: false, error: error.message };
        }
    }

    async signOut() {
        try {
            const supabase = getSupabaseClient();
            
            const { error } = await supabase.auth.signOut();
            if (error) throw error;

            this.currentUser = null;
            return { success: true };
        } catch (error) {
            console.error('Error signing out:', error);
            return { success: false, error: error.message };
        }
    }

    async getCurrentUser() {
        try {
            const supabase = getSupabaseClient();
            
            const { data: { user } } = await supabase.auth.getUser();
            this.currentUser = user;
            return user;
        } catch (error) {
            console.error('Error getting current user:', error);
            return null;
        }
    }

    async createProfile(userId, petData) {
        try {
            const supabase = getSupabaseClient();
            
            const { data, error } = await supabase
                .from('profiles')
                .insert([
                    {
                        id: userId,
                        pet_name: petData.petName,
                        pet_type: petData.petType,
                        pet_breed: petData.petBreed,
                        pet_age: petData.petAge,
                        description: petData.description,
                        owner_name: petData.ownerName,
                        owner_type: petData.ownerType, // 'individual' or 'foundation'
                        contact_info: petData.contactInfo,
                        created_at: new Date().toISOString()
                    }
                ]);

            if (error) throw error;
            return { success: true, data };
        } catch (error) {
            console.error('Error creating profile:', error);
            return { success: false, error: error.message };
        }
    }

    isAuthenticated() {
        return this.currentUser !== null;
    }
}

export const authService = new AuthService();