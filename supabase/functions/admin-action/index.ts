import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  try {
    const { pin, action, payload } = await req.json();

    const ADMIN_PIN = Deno.env.get("ADMIN_PIN");
    if (!ADMIN_PIN || pin !== ADMIN_PIN) {
      return new Response(JSON.stringify({ error: "PIN incorreto" }), {
        status: 401,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    // validate é só para checar o PIN — não precisa de DB
    if (action === "validate") {
      return new Response(JSON.stringify({ success: true }), {
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    const supabase = createClient(
      Deno.env.get("SUPABASE_URL")!,
      Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!
    );

    let error = null;

    switch (action) {
      case "complete_task":
        ({ error } = await supabase.from("tarefas").update({ status: "concluida" }).eq("id", payload.id));
        break;

      case "update_task":
        ({ error } = await supabase.from("tarefas").update({
          projeto_id: payload.projeto_id,
          descricao: payload.descricao,
          responsaveis: payload.responsaveis,
          data_inicio: payload.data_inicio,
          prazo: payload.prazo ?? null,
          prioridade: payload.prioridade,
        }).eq("id", payload.id));
        break;

      case "create_task":
        ({ error } = await supabase.from("tarefas").insert([{
          projeto_id: payload.projeto_id,
          descricao: payload.descricao,
          responsaveis: payload.responsaveis,
          status: "pendente",
          data_inicio: payload.data_inicio,
          prazo: payload.prazo ?? null,
          prioridade: payload.prioridade,
        }]));
        break;

      case "delete_task":
        ({ error } = await supabase.from("tarefas").update({ status: "excluida" }).eq("id", payload.id));
        break;

      case "restore_task":
      case "reopen_task":
        ({ error } = await supabase.from("tarefas").update({ status: "pendente" }).eq("id", payload.id));
        break;

      case "save_schedule": {
        if (payload.to_remove?.length > 0) {
          const { error: e } = await supabase.from("escalas").delete().in("id", payload.to_remove);
          if (e) { error = e; break; }
        }
        if (payload.to_add?.length > 0) {
          const { error: e } = await supabase.from("escalas").insert(
            payload.to_add.map((a: { dia_semana: number; hora_inicio: number; hora_fim: number }) => ({
              bolsista_id: payload.bolsista_id,
              dia_semana: a.dia_semana,
              hora_inicio: a.hora_inicio,
              hora_fim: a.hora_fim,
            }))
          );
          if (e) { error = e; }
        }
        break;
      }

      case "add_bolsista":
        ({ error } = await supabase.from("bolsistas").insert([{ nome: payload.nome, categoria: "Bolsista" }]));
        break;

      case "rename_bolsista":
        ({ error } = await supabase.from("bolsistas").update({ nome: payload.nome }).eq("id", payload.id));
        break;

      case "add_project":
        ({ error } = await supabase.from("projetos").insert([{ nome: payload.nome }]));
        break;

      case "save_notice":
        ({ error } = await supabase.from("configuracoes").upsert(
          { chave: "aviso_principal", valor: payload.valor },
          { onConflict: "chave" }
        ));
        break;

      default:
        return new Response(JSON.stringify({ error: "Ação desconhecida: " + action }), {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
    }

    if (error) {
      return new Response(JSON.stringify({ error: error.message }), {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    return new Response(JSON.stringify({ success: true }), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });

  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});
