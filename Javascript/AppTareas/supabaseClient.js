
// supabaseClient.js
import { createClient } from 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js/+esm';

const supabaseUrl = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx';
    const supabaseKey = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxAPI';
    const supabase = createClient(supabaseUrl, supabaseKey);

export default supabase;