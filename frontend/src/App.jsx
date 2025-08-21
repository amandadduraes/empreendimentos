import React, { useEffect, useMemo, useState } from "react";
import styled, { ThemeProvider, createGlobalStyle } from "styled-components";

const DEFAULT_API = "http://localhost:8000";

const theme = {
  colors: {
    text: "#111827",
    bg: "#f9fafb",
    card: "#ffffff",
    border: "#e5e7eb",
    primary: "#111827",
    muted: "#6b7280",
    successBg: "#dcfce7",
    successText: "#166534",
    errorBg: "#fee2e2",
    errorText: "#991b1b",
    warnBg: "#fff7ed",
    warnText: "#9a3412",
    headBg: "#f3f4f6",
  },
  radius: "12px",
};

const GlobalStyle = createGlobalStyle`
  * { box-sizing: border-box; }
  :root { color-scheme: light; }   
  body {
    margin: 0;
    background: ${(p) => p.theme.colors.bg};
    color: ${(p) => p.theme.colors.text};
    font-family: Inter, system-ui, Arial, sans-serif;
  }
`;

function isOkStatus(status) {
  return String(status || "").toLowerCase().startsWith("v");
}

export default function App() {
  const [apiBase, setApiBase] = useState(DEFAULT_API);
  const api = useMemo(() => apiBase.replace(/\/$/, ""), [apiBase]);

  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadEndpoint, setUploadEndpoint] = useState("/validar");
  const [uploadBusy, setUploadBusy] = useState(false);
  const [uploadError, setUploadError] = useState(null);
  const [uploadResponse, setUploadResponse] = useState(null);

  const [statusFilter, setStatusFilter] = useState("");
  const [listBusy, setListBusy] = useState(false);
  const [listError, setListError] = useState(null);
  const [listData, setListData] = useState([]);

  const [cidadeAudit, setCidadeAudit] = useState("");
  const [constrAudit, setConstrAudit] = useState("");
  const [opts, setOpts] = useState({ cidades: [], construtoras: [] });
  const [rulesAudit, setRulesAudit] = useState(null);
  const [auditBusy, setAuditBusy] = useState(false);
  const [auditError, setAuditError] = useState(null);



  useEffect(() => {
    if (!api) return;
    fetch(`${api}/regras-opcoes`)
      .then((r) => r.json())
      .then((data) => {
        setOpts({
          cidades: Array.isArray(data.cidades) ? data.cidades : [],
          construtoras: Array.isArray(data.construtoras) ? data.construtoras : [],
        });
      })
      .catch(() => {
      });
  }, [api]);


  async function onUploadSubmit(e) {
    e.preventDefault();
    setUploadError(null);
    setUploadResponse(null);
    if (!selectedFile) {
      setUploadError("Selecione um arquivo .json primeiro.");
      return;
    }
    setUploadBusy(true);
    try {
      const fd = new FormData();
      fd.append("file", selectedFile);
      const r = await fetch(`${api}${uploadEndpoint}`, { method: "POST", body: fd });
      const text = await r.text();
      let data;
      try {
        data = JSON.parse(text);
      } catch {
        data = { _raw: text };
      }
      if (!r.ok) throw new Error(typeof data === "object" && data?.detail ? data.detail : `HTTP ${r.status}`);
      setUploadResponse(data);
    } catch (e) {
      setUploadError(String(e));
    } finally {
      setUploadBusy(false);
    }
  }

  async function fetchList() {
    setListBusy(true);
    setListError(null);
    try {
      const url = new URL(`${api}/empreendimentos`);
      if (statusFilter) url.searchParams.set("status", statusFilter);
      const r = await fetch(url);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      setListData(await r.json());
    } catch (e) {
      setListError(String(e));
    } finally {
      setListBusy(false);
    }
  }

  const consultarRegras = async () => {
    if (!api) return alert("Defina a Base URL");
    setAuditBusy(true);
    setAuditError(null);
    setRulesAudit(null);
    try {
      const qs = new URLSearchParams();
      if (cidadeAudit) qs.append("cidade", cidadeAudit);
      if (constrAudit) qs.append("construtora", constrAudit);
      const res = await fetch(`${api}/regras-aplicadas?${qs.toString()}`);
      const json = await res.json();
      if (!res.ok) throw new Error(json?.detail || `HTTP ${res.status}`);
      setRulesAudit(json);
    } catch (err) {
      setAuditError(String(err));
    } finally {
      setAuditBusy(false);
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <GlobalStyle />
      <Container>
        <Header>
          <H1>Validador de Empreendimentos</H1>
        </Header>

        <Card>
          <H2>Upload de Arquivo (JSON)</H2>
          <Form onSubmit={onUploadSubmit}>
            <Row>
         

              <FileInput
                accept="application/json,.json"
                onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
              />
              <Button type="submit" disabled={uploadBusy}>
                {uploadBusy ? "Enviando..." : "Enviar"}
              </Button>
            </Row>
          </Form>
          {uploadError && <Alert $type="error">{uploadError}</Alert>}
          <UploadResult data={uploadResponse} />
        </Card>

        <Card>
          <H2>Regras aplicadas (auditoria)</H2>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr auto",
              gap: "12px",
              alignItems: "center",
            }}
          >
            <Select value={cidadeAudit} onChange={(e) => setCidadeAudit(e.target.value)}>
              <option value="">(Cidade — opcional)</option>
              {opts.cidades.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </Select>

            <Select value={constrAudit} onChange={(e) => setConstrAudit(e.target.value)}>
              <option value="">(Construtora — opcional)</option>
              {opts.construtoras.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </Select>

            <Button onClick={consultarRegras} disabled={auditBusy}>
              {auditBusy ? "Consultando..." : "Consultar"}
            </Button>
          </div>

          {auditError && <Alert $type="error" style={{ marginTop: 10 }}>{auditError}</Alert>}
          <div style={{ marginTop: 12 }}>
            <RulesView data={rulesAudit} />
          </div>
        </Card>

        <Footer>
          <hr />
          <Muted>
            Deixe o backend rodandos.
          </Muted>
        </Footer>
      </Container>
    </ThemeProvider>
  );
}

function UploadResult({ data }) {
  if (!data) return null;
  const isArray = Array.isArray(data);
  return (
    <div>
      {isArray ? (
        <ResultsTable rows={data} />
      ) : (
        <Box>
          <strong>Resposta:</strong> {typeof data === "object" ? JSON.stringify(data) : String(data)}
        </Box>
      )}
      <details>
        <summary>Ver JSON bruto</summary>
        <Pre>{JSON.stringify(data, null, 2)}</Pre>
      </details>
    </div>
  );
}

function ResultsTable({ rows }) {
  if (!rows?.length) return <Muted>Nenhum resultado.</Muted>;
  return (
    <TableWrap>
      <Table>
        <thead>
          <tr>
            <Th>Construtora</Th>
            <Th>Cidade</Th>
            <Th>Status</Th>
            <Th>Erros</Th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i}>
              <Td>{r.construtora}</Td>
              <Td>{r.cidade}</Td>
              <Td>
                <StatusPill $ok={isOkStatus(r.status)}>{r.status}</StatusPill>
              </Td>
              <Td>{r.erros?.length ? r.erros.join(", ") : "—"}</Td>
            </tr>
          ))}
        </tbody>
      </Table>
    </TableWrap>
  );
}

function ListTable({ rows }) {
  if (!rows?.length)
    return <Muted>Nada salvo ainda. Use /importar para gravar no banco.</Muted>;
  return (
    <TableWrap>
      <Table>
        <thead>
          <tr>
            <Th>ID</Th>
            <Th>Construtora</Th>
            <Th>Cidade</Th>
            <Th>Status</Th>
            <Th>Erros</Th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.id}>
              <Td>{r.id}</Td>
              <Td>{r.construtora}</Td>
              <Td>{r.cidade}</Td>
              <Td>
                <StatusPill $ok={isOkStatus(r.status)}>{r.status}</StatusPill>
              </Td>
              <Td>
                {r.erros?.length ? (
                  <details>
                    <summary>{r.erros.length} erro(s)</summary>
                    <ul style={{ margin: 0 }}>
                      {r.erros.map((e, i) => (
                        <li key={i}>{e}</li>
                      ))}
                    </ul>
                  </details>
                ) : (
                  "—"
                )}
              </Td>
            </tr>
          ))}
        </tbody>
      </Table>
    </TableWrap>
  );
}

function RulesView({ data }) {
  if (!data) return null;
  return (
    <div>
      <Muted>
        {data.default_city_rules ? (
          <em>Cidade não mapeada — usando conjunto padrão.</em>
        ) : (
          <em>Conjunto específico para a cidade.</em>
        )}
      </Muted>
      <RuleGroup title="Regras da cidade" items={data.city_rules} />
      <RuleGroup title="Regras da construtora" items={data.builder_rules} />
      <RuleGroup title="Regras combinadas (ordem de aplicação)" items={data.merged_rules} />
      <details>
        <summary>Ver JSON bruto</summary>
        <Pre>{JSON.stringify(data, null, 2)}</Pre>
      </details>
    </div>
  );
}

function RuleGroup({ title, items }) {
  if (!items?.length) return null;
  return (
    <div>
      <GroupTitle>{title}</GroupTitle>
      <Pills>
        {items.map((r) => (
          <Pill key={r.key} title={r.description}>
            {r.key}
          </Pill>
        ))}
      </Pills>
    </div>
  );
}

const Container = styled.div`
  max-width: 1100px;
  margin: 40px auto;
  padding: 0 16px;
`;
const Header = styled.header`
  margin-bottom: 24px;
`;
const Footer = styled.footer`
  margin: 32px 0 64px;
`;
const H1 = styled.h1`
  margin: 0 0 6px;
`;
const H2 = styled.h2`
  margin: 0 0 12px;
  font-size: 20px;
`;
const Muted = styled.p`
  margin: 6px 0 0;
  color: ${(p) => p.theme.colors.muted};
`;
const Card = styled.section`
  background: ${(p) => p.theme.colors.card};
  border: 1px solid ${(p) => p.theme.colors.border};
  border-radius: ${(p) => p.theme.radius};
  padding: 16px;
  margin-bottom: 16px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
`;
const Form = styled.form`
  margin-top: 8px;
  display: block;
`;
const Row = styled.div`
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
`;
const Label = styled.label`
  min-width: 80px;
  color: ${(p) => p.theme.colors.muted};
`;
const Input = styled.input`
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid ${(p) => p.theme.colors.border};
  background: #fff;
  min-width: 260px;
`;
const Select = styled.select`
  width: 100%;
  padding: 12px 14px;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  font-size: 14px;
  background: #fff;
  color: #111827;           
  color-scheme: light;      

  option {
    color: #111827;          
    background: #fff;       
  }
  option:disabled {
    color: #9ca3af;         
  }

  &:focus {
    outline: none;
    border-color: #111827;
    box-shadow: 0 0 0 3px rgba(17, 24, 39, .1);
  }
`;

const FileInput = styled.input.attrs({ type: "file" })``;
const Button = styled.button`
  padding: 10px 14px;
  border-radius: 10px;
  border: 1px solid ${(p) => p.theme.colors.border};
  background: ${(p) => p.theme.colors.primary};
  color: #fff;
  cursor: pointer;
  &:disabled {
    opacity: 0.6;
    cursor: default;
  }
`;

const Alert = styled.div`
  margin-top: 10px;
  padding: 12px;
  border-radius: 10px;
  font-size: 14px;
  background: ${(p) => (p.$type === "error" ? p.theme.colors.errorBg : p.theme.colors.warnBg)};
  color: ${(p) => (p.$type === "error" ? p.theme.colors.errorText : p.theme.colors.warnText)};
  border: 1px solid ${(p) => p.theme.colors.border};
`;
const Box = styled.div`
  padding: 12px;
  border: 1px solid ${(p) => p.theme.colors.border};
  border-radius: 10px;
  background: #fff;
  margin-top: 10px;
`;
const Pre = styled.pre`
  padding: 12px;
  border: 1px solid ${(p) => p.theme.colors.border};
  border-radius: 10px;
  background: #fff;
  overflow: auto;
`;
const TableWrap = styled.div`
  overflow: auto;
  border-radius: 10px;
  border: 1px solid ${(p) => p.theme.colors.border};
`;
const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
  background: #fff;
  th,
  td {
    padding: 10px 12px;
    border-bottom: 1px solid ${(p) => p.theme.colors.border};
    text-align: left;
  }
  thead th {
    background: ${(p) => p.theme.colors.headBg};
    font-weight: 600;
  }
`;
const Th = styled.th``;
const Td = styled.td``;
const StatusPill = styled.span`
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  background: ${(p) => (p.$ok ? p.theme.colors.successBg : p.theme.colors.errorBg)};
  color: ${(p) => (p.$ok ? p.theme.colors.successText : p.theme.colors.errorText)};
`;
const GroupTitle = styled.h3`
  margin: 16px 0 8px;
  font-size: 16px;
`;
const Pills = styled.div`
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
`;
const Pill = styled.span`
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid ${(p) => p.theme.colors.border};
  background: ${(p) => p.theme.colors.headBg};
  font-size: 12px;
`;
