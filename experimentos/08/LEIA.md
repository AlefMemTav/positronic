# Experimento 8 — retorno rápido após esquecimento

**Fase do roteiro:** Fase 3.
**Estado:** pré-registro e pipeline preparados; não executado.

O pré-registro está em `PREREGISTRO.md`. Nenhuma semente de calibração ou teste
foi aberta. Não há resultado a interpretar nesta versão.

## Fluxo previsto

1. Integrar o pré-registro antes de qualquer execução de calibração.
2. Em checkout limpo, executar `python3 experimentos/08/calibrar.py`.
3. Revisar e versionar `configuracao-congelada.json` e o registro
   `08-calibracao-*.json`. Se nenhum nível de ruído passar os gates, parar sem
   abrir sementes de teste.
4. Com a configuração de calibração commitada, executar
   `python3 experimentos/08/run_teste.py` uma única vez.
5. Versionar os registros primários antes de atualizar a conclusão deste arquivo
   e o estado do roadmap.

## Resultado

Pendente. A conclusão será preenchida depois do teste, qualquer que seja o
desfecho.
