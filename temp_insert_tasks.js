
const { createClient } = require('@supabase/supabase-js');

const SUPABASE_URL = 'https://vnodbsefjwvapvtdzgdl.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZub2Ric2Vmand2YXB2dGR6Z2RsIiwicm9sZES6ImFub24iLCJpYXQiOjE3NzMzNzI5NTMsImV4cCI6MjA4ODk0ODk1M30.M-7v57-obulKagTn-p5Pp6oKJWwcuu5FIvSLJ6andvs';

const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

async function addTasks() {
    // 1. Get Project ID for "Bloco de Motores"
    let { data: project } = await supabase.from('projetos').select('id').eq('nome', 'Bloco de Motores').maybeSingle();
    
    if (!project) {
        // Create if not exists
        const { data: newProj, error: pErr } = await supabase.from('projetos').insert([{ nome: 'Bloco de Motores' }]).select();
        if (pErr) { console.error("Error creating project:", pErr); return; }
        project = newProj[0];
    }
    
    console.log("Found Project ID:", project.id);

    const tasks = [
        { descricao: 'Trocador de calor', responsaveis: ["Caio Victor", "João Marcos"], status: 'atrasado', created_at: '2025-11-12' },
        { descricao: 'Conexões do motor', responsaveis: ["Laércio", "Lucas Duarte", "Sauã"], status: 'atrasado', created_at: '2025-11-12' },
        { descricao: 'Finalizar a bancada mono', responsaveis: ["Sauã", "Ryan", "Lucas Duarte", "João Guilherme"], status: 'atrasado', created_at: '2025-11-12' },
        { descricao: 'Instalação do dinamômetro da bancada mono', responsaveis: ["Sauã", "Ryan", "Lucas Duarte", "João Guilherme"], status: 'atrasado', created_at: '2025-12-06' },
        { descricao: 'Conexões gases de escape', responsaveis: ["Caio Victor", "João Marcos"], status: 'atrasado', created_at: '2025-11-17' },
        { descricao: 'Resfriamento do dinamômetro', responsaveis: ["Caio Victor", "João Marcos"], status: 'atrasado', created_at: '2025-12-01' }
    ].map(t => ({ ...t, projeto_id: project.id }));

    const { error } = await supabase.from('tarefas').insert(tasks);
    
    if (error) {
        console.error("Error inserting tasks:", error);
    } else {
        console.log("Success! 6 tasks added to 'Bloco de Motores'.");
    }
}

addTasks();
