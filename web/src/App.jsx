import { useEffect, useMemo, useState } from 'react'

const API_BASE = 'https://Jsnaldr.pythonanywhere.com'

const LOADING_MESSAGES = [
  'Membaca gejala yang kamu pilih…',
  'Membandingkan dengan pola gejala umum…',
  'Menyusun tiga kemungkinan teratas…',
]

const TENSI_OPTIONS = [
  { value: 'normal', label: 'Normal (≈120/80 atau lebih rendah)' },
  { value: 'agak_tinggi', label: 'Agak tinggi (120–139/80–89)' },
  { value: 'tinggi', label: 'Tinggi (140/90 ke atas)' },
]

const DURATION_OPTIONS = [
  { value: 'kurang_3_hari', label: 'Kurang dari 3 hari' },
  { value: '3_7_hari', label: '3–7 hari' },
  { value: '1_4_minggu', label: '1–4 minggu' },
  { value: 'lebih_1_bulan', label: 'Lebih dari 1 bulan' },
]

function Disclaimer({ compact }) {
  return (
    <div className={`disclaimer ${compact ? 'compact' : ''}`}>
      <span className="disclaimer-icon">ⓘ</span>
      <p>
        <strong>Ini bukan diagnosis medis.</strong> BINUS Disease Detection adalah alat skrining
        awal untuk keperluan edukasi/portofolio. Hasilnya adalah kemungkinan berdasarkan pola
        gejala umum — selalu konsultasikan kondisi kamu ke dokter untuk diagnosis dan penanganan
        yang sesungguhnya.
      </p>
    </div>
  )
}

function OptionalChoiceRow({ title, options, value, onChange }) {
  // value bisa: null (belum dipilih), 'skip' (tidak tahu/tidak mau jawab), atau salah satu option value
  return (
    <div className="optional-block">
      <h3>{title}</h3>
      <div className="chip-grid">
        {options.map((opt) => (
          <button
            key={opt.value}
            type="button"
            className={`chip ${value === opt.value ? 'active' : ''}`}
            onClick={() => onChange(opt.value)}
          >
            {opt.label}
          </button>
        ))}
        <button
          type="button"
          className={`chip chip-skip ${value === 'skip' ? 'active' : ''}`}
          onClick={() => onChange('skip')}
        >
          Tidak tahu
        </button>
        <button
          type="button"
          className={`chip chip-skip ${value === 'skip-refuse' ? 'active' : ''}`}
          onClick={() => onChange('skip-refuse')}
        >
          Tidak mau jawab
        </button>
      </div>
    </div>
  )
}

function AgeInput({ age, onAgeChange, skipped, onSkipToggle }) {
  return (
    <div className="optional-block">
      <h3>Umur (opsional)</h3>
      <div className="bmi-row">
        <label className="bmi-field">
          <span>Umur (tahun)</span>
          <input
            type="number"
            min="0"
            max="120"
            placeholder="mis. 28"
            value={age}
            disabled={skipped}
            onChange={(e) => onAgeChange(e.target.value)}
          />
        </label>
      </div>
      <div className="chip-grid" style={{ marginTop: 10 }}>
        <button type="button" className={`chip chip-skip ${skipped ? 'active' : ''}`} onClick={onSkipToggle}>
          {skipped ? '✓ Tidak diisi' : 'Tidak tahu / tidak mau menjawab'}
        </button>
      </div>
    </div>
  )
}

function BmiInput({ bb, tb, onBbChange, onTbChange, skipped, onSkipToggle }) {
  return (
    <div className="optional-block">
      <h3>Berat &amp; tinggi badan (opsional, untuk hitung BMI)</h3>
      <div className="bmi-row">
        <label className="bmi-field">
          <span>Berat badan (kg)</span>
          <input
            type="number"
            min="1"
            max="400"
            placeholder="mis. 60"
            value={bb}
            disabled={skipped}
            onChange={(e) => onBbChange(e.target.value)}
          />
        </label>
        <label className="bmi-field">
          <span>Tinggi badan (cm)</span>
          <input
            type="number"
            min="50"
            max="250"
            placeholder="mis. 165"
            value={tb}
            disabled={skipped}
            onChange={(e) => onTbChange(e.target.value)}
          />
        </label>
      </div>
      <div className="chip-grid" style={{ marginTop: 10 }}>
        <button type="button" className={`chip chip-skip ${skipped ? 'active' : ''}`} onClick={onSkipToggle}>
          {skipped ? '✓ Tidak diisi' : 'Tidak tahu / tidak mau menjawab'}
        </button>
      </div>
    </div>
  )
}

function SymptomGroup({ title, symptoms, selected, onToggle }) {
  return (
    <div className="symptom-group">
      <h3>{title}</h3>
      <div className="chip-grid">
        {Object.entries(symptoms).map(([key, label]) => {
          const isActive = selected.has(key)
          return (
            <button
              key={key}
              type="button"
              className={`chip ${isActive ? 'active' : ''}`}
              onClick={() => onToggle(key)}
              aria-pressed={isActive}
            >
              {label}
            </button>
          )
        })}
      </div>
    </div>
  )
}

function LoadingView({ message }) {
  return (
    <div className="loading-view">
      <div className="spinner" />
      <p>{message}</p>
    </div>
  )
}

function ResultCard({ result, rank }) {
  const pct = Math.round(result.probability * 100)
  return (
    <div className={`result-card ${result.urgent ? 'urgent' : ''}`}>
      <div className="result-top">
        <span className="rank-badge">#{rank}</span>
        <div className="result-title">
          <h3>{result.disease}</h3>
          <span className="category-tag">{result.category}</span>
        </div>
        <span className="prob-value">{pct}%</span>
      </div>
      <div className="prob-track">
        <div className="prob-fill" style={{ width: `${pct}%` }} />
      </div>
      <p className="result-desc">{result.description}</p>
      {result.contributing_symptoms?.length > 0 && (
        <div className="contributing-row">
          <span className="specialist-label">Gejala paling khas dari yang kamu pilih:</span>
          <div className="contributing-chips">
            {result.contributing_symptoms.map((c) => (
              <span key={c.symptom} className="contributing-chip">{c.label}</span>
            ))}
          </div>
        </div>
      )}
      <div className="specialist-row">
        <span className="specialist-label">Disarankan konsultasi ke:</span>
        <span className="specialist-badge">{result.specialist}</span>
      </div>
    </div>
  )
}

function ResultsView({ data, onReset }) {
  return (
    <div className="results-view">
      {data.urgent_warning && (
        <div className="urgent-banner">
          <strong>⚠ Perhatian:</strong> {data.urgent_message}
        </div>
      )}

      <h2>Tiga kemungkinan teratas</h2>
      <p className="results-sub">
        Berdasarkan {data.input_symptoms.length} gejala
        {data.bmi_category_used !== 'tidak_tahu' && `, BMI kategori "${data.bmi_category_used}"`}
        {data.tensi_category_used !== 'tidak_tahu' && `, tensi "${data.tensi_category_used}"`}
        {data.duration_category_used !== 'tidak_tahu' && `, durasi "${data.duration_category_used.replaceAll('_', ' ')}"`}
        .
      </p>

      <div className="results-list">
        {data.top_predictions.map((r, i) => (
          <ResultCard key={r.disease} result={r} rank={i + 1} />
        ))}
      </div>

      <Disclaimer />

      <button className="reset-btn" onClick={onReset}>Cek gejala lain</button>
    </div>
  )
}

// value chip: null | 'skip' | 'skip-refuse' | kode_kategori -> dikonversi ke payload API
function resolveChoice(value) {
  if (!value || value === 'skip' || value === 'skip-refuse') return null
  return value
}

export default function App() {
  const [groups, setGroups] = useState(null)
  const [selected, setSelected] = useState(new Set())
  const [bb, setBb] = useState('')
  const [tb, setTb] = useState('')
  const [bbTbSkipped, setBbTbSkipped] = useState(false)
  const [age, setAge] = useState('')
  const [ageSkipped, setAgeSkipped] = useState(false)
  const [tensiChoice, setTensiChoice] = useState(null)
  const [durationChoice, setDurationChoice] = useState(null)
  const [stage, setStage] = useState('intake')
  const [loadingMsg, setLoadingMsg] = useState(LOADING_MESSAGES[0])
  const [results, setResults] = useState(null)
  const [errorMsg, setErrorMsg] = useState('')

  useEffect(() => {
    fetch(`${API_BASE}/symptoms`)
      .then((r) => r.json())
      .then((data) => setGroups(data.groups))
      .catch(() => setErrorMsg('Gagal memuat daftar gejala. Pastikan API server (uvicorn) sedang berjalan.'))
  }, [])

  const selectedCount = selected.size

  function toggleSymptom(key) {
    setSelected((prev) => {
      const next = new Set(prev)
      if (next.has(key)) next.delete(key)
      else next.add(key)
      return next
    })
  }

  async function handleSubmit() {
    if (selectedCount === 0) return
    setStage('loading')
    setErrorMsg('')

    let msgIndex = 0
    const interval = setInterval(() => {
      msgIndex = (msgIndex + 1) % LOADING_MESSAGES.length
      setLoadingMsg(LOADING_MESSAGES[msgIndex])
    }, 700)

    const minDelay = new Promise((res) => setTimeout(res, 1600))

    const payload = {
      symptoms: Array.from(selected),
      berat_badan_kg: bbTbSkipped || !bb ? null : Number(bb),
      tinggi_badan_cm: bbTbSkipped || !tb ? null : Number(tb),
      tensi_category: resolveChoice(tensiChoice),
      duration_category: resolveChoice(durationChoice),
      umur_tahun: ageSkipped || !age ? null : Number(age),
    }

    try {
      const [response] = await Promise.all([
        fetch(`${API_BASE}/predict`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        }),
        minDelay,
      ])
      clearInterval(interval)

      if (!response.ok) throw new Error('Request gagal')
      const data = await response.json()
      setResults(data)
      setStage('results')
    } catch (err) {
      clearInterval(interval)
      setErrorMsg('Gagal menghubungi API. Pastikan server (uvicorn) sedang berjalan di port 8010.')
      setStage('error')
    }
  }

  function handleReset() {
    setSelected(new Set())
    setBb(''); setTb(''); setBbTbSkipped(false)
    setAge(''); setAgeSkipped(false)
    setTensiChoice(null); setDurationChoice(null)
    setResults(null)
    setStage('intake')
  }

  const totalSymptoms = useMemo(() => {
    if (!groups) return 0
    return Object.values(groups).reduce((sum, g) => sum + Object.keys(g).length, 0)
  }, [groups])

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark">+</span>
          <div>
            <h1>BINUS Disease Detection</h1>
            <p className="tagline">Skrining awal gejala &amp; arahan dokter spesialis</p>
          </div>
        </div>
      </header>

      <Disclaimer compact />

      <main className="main-content">
        {stage === 'intake' && (
          <>
            <div className="intake-head">
              <h2>Sedikit data tambahan (boleh dilewati)</h2>
              <p>Membantu hasil lebih relevan — tapi kamu bebas pilih "tidak tahu" atau "tidak mau jawab" kapan saja.</p>
            </div>

            <BmiInput
              bb={bb} tb={tb}
              onBbChange={setBb} onTbChange={setTb}
              skipped={bbTbSkipped}
              onSkipToggle={() => { setBbTbSkipped((s) => !s); setBb(''); setTb('') }}
            />
            <AgeInput
              age={age} onAgeChange={setAge}
              skipped={ageSkipped}
              onSkipToggle={() => { setAgeSkipped((s) => !s); setAge('') }}
            />
            <OptionalChoiceRow title="Tekanan darah (tensi), kalau tahu" options={TENSI_OPTIONS} value={tensiChoice} onChange={setTensiChoice} />
            <OptionalChoiceRow title="Sudah berapa lama merasakan gejala ini?" options={DURATION_OPTIONS} value={durationChoice} onChange={setDurationChoice} />

            <div className="intake-head" style={{ marginTop: 8 }}>
              <h2>Pilih gejala yang kamu rasakan</h2>
              <p>{totalSymptoms > 0 ? `${totalSymptoms} gejala tersedia, boleh pilih lebih dari satu.` : 'Memuat daftar gejala…'}</p>
            </div>

            {errorMsg && <div className="error-banner">{errorMsg}</div>}

            {groups && Object.entries(groups).map(([title, symptoms]) => (
              <SymptomGroup key={title} title={title} symptoms={symptoms} selected={selected} onToggle={toggleSymptom} />
            ))}

            <div className="submit-bar">
              <span>{selectedCount} gejala dipilih</span>
              <button className="submit-btn" disabled={selectedCount === 0} onClick={handleSubmit}>
                Lihat kemungkinan
              </button>
            </div>
          </>
        )}

        {stage === 'loading' && <LoadingView message={loadingMsg} />}

        {stage === 'results' && results && <ResultsView data={results} onReset={handleReset} />}

        {stage === 'error' && (
          <div className="error-banner">
            {errorMsg}
            <button className="reset-btn" onClick={() => setStage('intake')}>Kembali</button>
          </div>
        )}
      </main>

      <footer className="footer">
        Dibuat untuk keperluan portofolio &amp; edukasi — bukan produk medis resmi.
      </footer>
    </div>
  )
}
