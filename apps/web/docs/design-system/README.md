# ContaAI Product UI v1

Pagina de login este sursa limbajului vizual pentru întregul produs.

## Principii
- suprafețe luminoase, translucide, cu umbre discrete;
- gradient violet/albastru rezervat acțiunilor și zonelor AI;
- radius generos (12–26px);
- spațiere aerisită și ierarhie tipografică clară;
- backend-ul rămâne autoritatea pentru permisiuni;
- AI local (Ollama pe GTX 1080 Ti) este prezentat ca motor de analiză, nu ca sursă contabilă definitivă.

## Componente CSS v1
- `.ca-button` + variante `primary`, `secondary`, `light`
- `.ca-icon-button`
- `.ca-select-shell`
- `.ca-panel`
- `.ca-kpi`
- `.ca-modal`
- `.ca-form`
- `.ca-role-pill`
- `.ca-note`

## Ecrane incluse
- Dashboard
- Workspace
- Companies
- Members (UI pregătit; invitațiile necesită API)
- Navigație desktop și mobil

## Reguli
1. Nu se creează un nou stil de buton direct într-o pagină.
2. Operațiile sensibile trebuie validate în backend chiar dacă UI ascunde sau dezactivează acțiunea.
3. Datele demo din dashboard vor fi înlocuite gradual cu valori API reale.
4. Dark mode trebuie păstrat pentru fiecare componentă nouă.
