import { useEffect, useState } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { api, getToken } from "../../lib/api";
import { DashboardLayout, useToast } from "../../components/ui";
import { IconBuilding, IconUpload, IconSearch, IconBriefcase } from "../../components/icons";
import ImageUpload from "../../components/ImageUpload";
import { AIResult, AIList, useAI, useAICall } from "../../components/AIPanel";
import { Combobox, TagInput } from "../../components/fields";
import { CATEGORIES, CITIES, EXPERIENCE, SALARY, SKILLS } from "../../lib/options";
import { IconSparkle } from "../../components/icons";

const MENU = [
  { to: "/institute", label: "Profile", icon: IconBuilding },
  { to: "/institute/upload", label: "Data upload", icon: IconUpload },
  { to: "/institute/students", label: "Student search", icon: IconSearch },
  { to: "/institute/post-job", label: "Post a job", icon: IconBriefcase },
];

export default function Institute() {
  return (
    <DashboardLayout title="Institute" menu={MENU}>
      <Routes>
        <Route index element={<Profile />} />
        <Route path="upload" element={<DataUpload />} />
        <Route path="students" element={<StudentSearch />} />
        <Route path="post-job" element={<PostJob />} />
        <Route path="*" element={<Navigate to="/institute" replace />} />
      </Routes>
    </DashboardLayout>
  );
}

function Profile() {
  const [p, setP] = useState(null);
  useEffect(() => { api.get("/api/institute/profile").then(setP).catch(() => {}); }, []);
  if (!p) return <p>Loading…</p>;
  return (
    <div className="max-w-2xl">
      <h2 className="mb-5 text-xl font-bold text-navy">{p.name}</h2>
      <div className="card mb-5">
        <h3 className="mb-3 font-semibold text-slate-700">Institute logo</h3>
        <ImageUpload kind="logo" round={false} currentUrl={p.logo_url}
                     onUploaded={(u) => setP({ ...p, logo_url: u })} />
      </div>
      <div className="card space-y-1 text-sm">
        <Row k="Email" v={p.email} />
        <Row k="Phone" v={p.phone} />
        <Row k="City / State" v={`${p.city || "—"}, ${p.state || "—"}`} />
        <Row k="Country" v={p.country} />
        <Row k="Promoter" v={p.promoter_name} />
        <Row k="Authorised person" v={p.authorised_person_name} />
        <Row k="Courses" v={(p.courses || []).join(", ")} />
        <Row k="Strength" v={p.present_strength} />
        <Row k="Website" v={p.website} />
      </div>
    </div>
  );
}

/* THE emphasized flow: upload Excel -> auto resumes -> emailed credentials */
function DataUpload() {
  const toast = useToast();
  const [file, setFile] = useState(null);
  const [busy, setBusy] = useState(false);
  const [results, setResults] = useState(null);

  const downloadTemplate = async () => {
    // fetch with auth then trigger a browser download
    const res = await fetch("/api/institute/upload-template", {
      headers: { Authorization: `Bearer ${getToken()}` },
    });
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = "hire_student_upload_template.xlsx"; a.click();
    URL.revokeObjectURL(url);
  };

  const upload = async () => {
    if (!file) return toast("Choose an Excel file first.", "error");
    setBusy(true);
    try {
      const res = await api.upload("/api/institute/upload", file);
      setResults(res.results);
      toast(res.message);
    } catch (err) {
      toast(err.message, "error");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="max-w-3xl">
      <h1 className="mb-2 text-xl font-semibold">Data upload</h1>
      <p className="mb-4 text-sm text-gray-600">
        Upload an Excel of one or many students. A resume is auto-created from the available
        columns, stored in the database, and each student is emailed their login credentials.
      </p>

      <div className="card">
        <button className="btn-outline mb-4" onClick={downloadTemplate}>Download template</button>
        <div className="flex items-center gap-3">
          <input type="file" accept=".xlsx,.xls" onChange={(e) => setFile(e.target.files[0])} />
          <button className="btn" onClick={upload} disabled={busy}>
            {busy ? "Uploading…" : "Upload & create accounts"}
          </button>
        </div>
      </div>

      {results && (
        <div className="card mt-4">
          <h2 className="mb-2 font-semibold">Result</h2>
          <table className="table">
            <thead><tr><th>Student</th><th>User ID</th><th>Password</th><th>Status</th></tr></thead>
            <tbody>
              {results.map((r, i) => (
                <tr key={i}>
                  <td>{r.row}</td>
                  <td>{r.user_id || "—"}</td>
                  <td>{r.password || "—"}</td>
                  <td>{r.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <p className="mt-2 text-xs text-gray-500">
            Passwords are shown once here for your reference; students also receive them by email.
          </p>
        </div>
      )}
    </div>
  );
}

function StudentSearch() {
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [rows, setRows] = useState([]);

  const search = async () => {
    const params = new URLSearchParams();
    if (email) params.set("email", email);
    if (phone) params.set("phone", phone);
    setRows(await api.get(`/api/institute/students?${params}`));
  };
  useEffect(() => { search(); }, []);

  return (
    <div>
      <h1 className="mb-4 text-xl font-semibold">Student search</h1>
      <div className="mb-4 flex flex-wrap gap-2">
        <input className="input max-w-xs" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
        <input className="input max-w-xs" placeholder="Phone" value={phone} onChange={(e) => setPhone(e.target.value)} />
        <button className="btn" onClick={search}>Search</button>
      </div>
      <table className="table">
        <thead><tr><th>Name</th><th>Email</th><th>Phone</th><th>Location</th><th>Key skills</th></tr></thead>
        <tbody>
          {rows.map((s) => (
            <tr key={s.id}>
              <td>{`${s.first_name || ""} ${s.last_name || ""}`.trim() || "—"}</td>
              <td>{s.email}</td>
              <td>{s.phone}</td>
              <td>{s.location}</td>
              <td>{(s.key_skills || []).join(", ")}</td>
            </tr>
          ))}
          {rows.length === 0 && <tr><td colSpan={5} className="text-gray-500">No students found.</td></tr>}
        </tbody>
      </table>
    </div>
  );
}

function PostJob() {
  const toast = useToast();
  const { enabled: aiOn } = useAI();
  const { call, busy: aiBusy } = useAICall();
  const [form, setForm] = useState({ contact_visible: true, key_skills: [] });
  const [aiDraft, setAiDraft] = useState(null);
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });
  const setV = (k) => (v) => setForm({ ...form, [k]: v });

  const draftWithAI = async () => {
    if (!form.title?.trim()) return toast("Enter a job title first.", "error");
    const r = await call("/api/ai/job/describe", {
      title: form.title, location: form.location, category: form.category,
      experience: form.experience, salary: form.salary, skills: form.key_skills,
    });
    if (r) setAiDraft(r);
  };
  const applyDraft = () => {
    setForm({ ...form, description: aiDraft.description || form.description,
      requirement_education: aiDraft.requirement_education || form.requirement_education,
      requirement_technical: aiDraft.requirement_technical || form.requirement_technical,
      key_skills: aiDraft.key_skills?.length ? aiDraft.key_skills : form.key_skills });
    setAiDraft(null); toast("Draft applied — edit before posting.");
  };

  const submit = async () => {
    try {
      await api.post("/api/institute/jobs", { ...form, key_skills: form.key_skills || [] });
      toast(`Your job posting for "${form.title}" has been posted successfully.`);
      setForm({ contact_visible: true, key_skills: [] });
    } catch (err) { toast(err.message, "error"); }
  };

  return (
    <div className="max-w-2xl">
      <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-xl font-bold text-navy">Post a job</h2>
        {aiOn && (
          <button className="btn-outline btn-sm" onClick={draftWithAI} disabled={aiBusy}>
            <IconSparkle size={14} /> {aiBusy ? "Drafting…" : "Draft with AI"}
          </button>
        )}
      </div>
      <div className="card grid gap-4 sm:grid-cols-2">
        <div className="sm:col-span-2"><label className="label">Job title *</label>
          <input className="input" value={form.title || ""} onChange={set("title")} /></div>
        <div><label className="label">Job code</label><input className="input" value={form.job_code || ""} onChange={set("job_code")} /></div>
        <Combobox label="Location" value={form.location} options={CITIES} onChange={setV("location")} />
        <Combobox label="Category" value={form.category} options={CATEGORIES} onChange={setV("category")} aiField="job category" />
        <Combobox label="Experience" value={form.experience} options={EXPERIENCE} onChange={setV("experience")} />
        <Combobox label="Salary" value={form.salary} options={SALARY} onChange={setV("salary")} />
        <div className="sm:col-span-2">
          <TagInput label="Key skills" values={form.key_skills || []} options={SKILLS} onChange={setV("key_skills")} />
        </div>
        {aiDraft && (
          <div className="sm:col-span-2">
            <AIResult title="AI draft" onClose={() => setAiDraft(null)}>
              <p className="whitespace-pre-line leading-relaxed">{aiDraft.description}</p>
              <AIList label="Responsibilities" items={aiDraft.responsibilities} />
              <button className="btn-green btn-sm mt-3" onClick={applyDraft}>Use this draft</button>
            </AIResult>
          </div>
        )}
        <div className="sm:col-span-2"><label className="label">Description</label>
          <textarea className="input" rows={5} value={form.description || ""} onChange={set("description")} /></div>
        <div className="sm:col-span-2"><button className="btn" onClick={submit}>Post job</button></div>
      </div>
    </div>
  );
}

function Row({ k, v }) {
  return <div className="flex justify-between border-b border-gray-100 py-1"><span className="text-gray-500">{k}</span><span>{v || "—"}</span></div>;
}
function F({ label, onChange, span }) {
  return <div className={span ? "sm:col-span-2" : ""}><label className="label">{label}</label><input className="input" onChange={onChange} /></div>;
}
