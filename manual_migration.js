
const { createClient } = require('@supabase/supabase-js');

const SUPABASE_URL = 'https://vnodbsefjwvapvtdzgdl.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZub2Ric2Vmand2YXB2dGR6Z2RsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzMzNzI5NTMsImV4cCI6MjA4ODk0ODk1M30.M-7v57-obulKagTn-p5Pp6oKJWwcuu5FIvSLJ6andvs';

const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

async function run() {
    const { data: bolsistas } = await supabase.from('bolsistas').select('*');
    const bMap = {};
    bolsistas.forEach(b => {
        const nomeLimpo = b.nome.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().trim();
        bMap[nomeLimpo] = b.id;
    });

    const escalas = [];

    function add(nome, dia, inicio, fim) {
        const nomeLimpo = nome.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().trim();
        const id = bMap[nomeLimpo];
        if (id) {
            for (let h = inicio; h < fim; h++) {
                if (h === 12) continue; // ORDONES / Almoço
                escalas.push({ bolsista_id: id, dia_semana: dia, hora_inicio: h, hora_fim: h + 1 });
            }
        }
    }

    // SEGUNDA (1)
    add('João Marcos', 1, 8, 12); add('João Marcos', 1, 13, 17);
    add('Lucas Duarte', 1, 8, 12); add('Lucas Duarte', 1, 13, 17);
    add('Ryan', 1, 8, 12);
    add('Lucas Cruz', 1, 8, 12); add('Lucas Cruz', 1, 13, 17);
    add('Julia', 1, 10, 12); add('Julia', 1, 13, 17);
    add('Caio', 1, 8, 12); add('Caio', 1, 13, 17);
    add('Sauã', 1, 10, 11); add('Sauã', 1, 13, 16);
    add('João Guilherme', 1, 13, 18);

    // TERÇA (2)
    add('João Marcos', 2, 8, 12); add('João Marcos', 2, 13, 16);
    add('Lucas Duarte', 2, 8, 12); add('Lucas Duarte', 2, 13, 16);
    add('Ryan', 2, 8, 12);
    add('Ruy', 2, 8, 11); add('Ruy', 2, 13, 17);
    add('Sauã', 2, 10, 12); add('Sauã', 2, 13, 17);
    add('Lucas Cruz', 2, 10, 12); add('Lucas Cruz', 2, 13, 17);
    add('João Guilherme', 2, 13, 18);
    add('Clara', 2, 13, 18);
    add('Julia', 2, 13, 17);

    // QUARTA (3)
    add('Ryan', 3, 8, 12);
    add('Lucas Duarte', 3, 9, 12);
    add('Lucas Cruz', 3, 9, 12);
    add('Ruy', 3, 8, 12); add('Ruy', 3, 13, 16);
    add('Caio', 3, 8, 12); add('Caio', 3, 13, 17);
    add('João Marcos', 3, 10, 12); add('João Marcos', 3, 13, 16);
    add('Julia', 3, 10, 12); add('Julia', 3, 13, 17);
    add('João Guilherme', 3, 13, 17);
    add('Clara', 3, 13, 17);
    add('Sauã', 3, 13, 16);

    // QUINTA (4)
    add('Ryan', 4, 8, 12);
    add('Caio', 4, 8, 12); add('Caio', 4, 13, 18);
    add('Ruy', 4, 8, 12); add('Ruy', 4, 13, 17);
    add('Sauã', 4, 10, 12); add('Sauã', 4, 13, 16);
    add('João Guilherme', 4, 13, 16);
    add('Clara', 4, 13, 18);
    add('Julia', 4, 13, 17);

    // SEXTA (5)
    add('João Guilherme', 5, 8, 12); add('João Guilherme', 5, 13, 16);
    add('João Marcos', 5, 8, 12); add('João Marcos', 5, 13, 16);
    add('Lucas Duarte', 5, 8, 12); add('Lucas Duarte', 5, 13, 16);
    add('Lucas Cruz', 5, 8, 12); add('Lucas Cruz', 5, 13, 16);
    add('Ruy', 5, 8, 12); add('Ruy', 5, 13, 17);
    add('Caio', 5, 8, 12); add('Caio', 5, 13, 16);
    add('Clara', 5, 10, 12); add('Clara', 5, 13, 17);
    add('Ryan', 5, 10, 12);
    add('Sauã', 5, 13, 16);

    console.log(`Total de entradas: ${escalas.length}`);
    
    // Limpar e inserir
    await supabase.from('escalas').delete().neq('id', '00000000-0000-0000-0000-000000000000');
    
    const { error } = await supabase.from('escalas').insert(escalas);
    if (error) console.error(error);
    else console.log('Escalas inseridas com sucesso!');
}

run();
