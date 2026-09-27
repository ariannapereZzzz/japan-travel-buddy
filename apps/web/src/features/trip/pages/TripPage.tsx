import { useMemo, useState } from "react";
import { useTrip } from "@/features/trip/hooks/useTrip";
import { formatMoney } from "@/features/trip/lib/money";
import type {
  ExpenseInput,
  Flight,
  TransportLeg,
  Trip,
} from "@/features/trip/lib/types";

const tabs = [
  ["summary", "Summary"],
  ["itinerary", "Itinerary"],
  ["transport", "Transport"],
  ["packing", "Packing"],
  ["tips", "Tips"],
  ["notes", "Notes"],
] as const;

type Tab = (typeof tabs)[number][0];

export function TripPage() {
  const tripApi = useTrip();
  const [tab, setTab] = useState<Tab>("itinerary");
  const { trip, isLoading, isError } = tripApi;

  return (
    <>
      <div className="bg-texture" />
      <div className="app">
        <header className="hero">
          <div className="eyebrow">
            {trip?.eyebrow ?? "日本 · Trip Manager"}
          </div>
          <h1>{trip?.title ?? "Japan 2026"}</h1>
          <div className="dates">
            {trip?.date_label ?? "September 30 – October 14"}
          </div>
          <div className="route">
            {(trip?.route ?? []).map((stop, index) => (
              <span key={stop}>
                <span className="node">{stop}</span>
                {index < (trip?.route.length ?? 0) - 1 ? (
                  <span className="arrow"> → </span>
                ) : null}
              </span>
            ))}
          </div>
        </header>
        <nav className="tabs">
          {tabs.map(([id, label]) => (
            <button
              key={id}
              type="button"
              className={tab === id ? "active" : undefined}
              onClick={() => setTab(id)}
            >
              {label}
            </button>
          ))}
        </nav>
        <main>
          {isLoading ? <p className="status-line">Loading trip…</p> : null}
          {isError ? (
            <p className="status-line">
              Could not load the trip.{" "}
              <button type="button" onClick={tripApi.refetch}>
                Retry
              </button>
            </p>
          ) : null}
          {trip && tab === "summary" ? <SummaryPanel trip={trip} /> : null}
          {trip && tab === "itinerary" ? (
            <ItineraryPanel trip={trip} api={tripApi} />
          ) : null}
          {trip && tab === "transport" ? <TransportPanel trip={trip} /> : null}
          {trip && tab === "packing" ? (
            <PackingPanel trip={trip} api={tripApi} />
          ) : null}
          {trip && tab === "tips" ? <TipsPanel trip={trip} /> : null}
          {trip && tab === "notes" ? (
            <NotesPanel trip={trip} api={tripApi} />
          ) : null}
        </main>
        <footer className="credit">Checkboxes save automatically.</footer>
        {tripApi.saveError ? (
          <p className="save-error">Could not save. Try again.</p>
        ) : null}
      </div>
    </>
  );
}

type TripApi = ReturnType<typeof useTrip>;

function SummaryPanel({ trip }: { trip: Trip }) {
  return (
    <>
      <h2 className="section-title">Hotel booking dates</h2>
      {trip.hotels.map((hotel) => (
        <article key={hotel.id} className="hotel-card">
          <div className="h-city">{hotel.city}</div>
          <div className="hotel-row">
            <span className="h-label">Check-in</span>
            <span className="h-value">{hotel.check_in}</span>
          </div>
          <div className="hotel-row">
            <span className="h-label">Check-out</span>
            <span className="h-value">{hotel.check_out}</span>
          </div>
          <span className="hotel-nights">
            {hotel.nights} night{hotel.nights > 1 ? "s" : ""}
          </span>
        </article>
      ))}
      <h2 className="section-title section-gap">Flights</h2>
      {trip.flight_groups.map((group) => (
        <article key={group.label} className="flight-summary-card">
          <div className="fs-title">{group.label}</div>
          {group.legs.map((leg) => (
            <FlightRow key={`${leg.origin}-${leg.depart_time}`} flight={leg} />
          ))}
        </article>
      ))}
    </>
  );
}

function ItineraryPanel({ trip, api }: { trip: Trip; api: TripApi }) {
  const [open, setOpen] = useState<Record<string, boolean>>({});
  const { done, total } = useMemo(() => {
    const tasks = trip.days.flatMap((day) => day.tasks);
    return {
      total: tasks.length,
      done: tasks.filter((task) => task.checked).length,
    };
  }, [trip.days]);

  return (
    <>
      <Progress label={`${done} / ${total} done`} total={total} done={done} />
      {trip.days.map((day) => (
        <article
          key={day.id}
          className={open[day.id] ? "day-card open" : "day-card"}
        >
          <button
            type="button"
            className="day-head"
            onClick={() =>
              setOpen((current) => ({ ...current, [day.id]: !current[day.id] }))
            }
          >
            <div className="day-num">{day.date_label}</div>
            <div className="day-info">
              <div className="d-title">{day.title}</div>
              <div className="d-sub">{day.subtitle}</div>
            </div>
            <div className="day-chevron">▶</div>
          </button>
          <div className="day-body">
            {day.flights.length > 0 ? (
              <div className="inline-flights">
                <div className="if-head">Flights</div>
                {day.flights.map((flight) => (
                  <FlightRow
                    key={`${flight.origin}-${flight.depart_time}`}
                    flight={flight}
                  />
                ))}
              </div>
            ) : null}
            {day.leg ? <InlineLeg leg={day.leg} /> : null}
            {!day.leg && day.transit ? (
              <div className="transit-chip">{day.transit}</div>
            ) : null}
            {day.tasks.map((task) => (
              <CheckRow
                key={task.id}
                id={task.id}
                label={task.body}
                checked={task.checked}
                onChange={(checked) => api.toggleTask(task.id, checked)}
              />
            ))}
          </div>
        </article>
      ))}
      <div className="reset-row">
        <button type="button" onClick={api.resetItinerary}>
          Reset itinerary checkboxes
        </button>
      </div>
    </>
  );
}

function TransportPanel({ trip }: { trip: Trip }) {
  return (
    <>
      {trip.callout ? (
        <div className="callout">
          <h3>{trip.callout.title}</h3>
          <p>{trip.callout.body}</p>
        </div>
      ) : null}
      {trip.legs.map((leg) => (
        <article key={leg.id} className="leg-card">
          <div className="leg-route">
            <span className="from">{leg.origin}</span>
            <span className="sep">→</span>
            <span className="to">{leg.destination}</span>
          </div>
          <div className="leg-meta">
            <b>{leg.mode}</b> · {leg.duration}
          </div>
          <div className="leg-detail">
            <p>{leg.detail}</p>
            {leg.detail_extra ? (
              <p style={{ marginTop: 8 }}>{leg.detail_extra}</p>
            ) : null}
          </div>
          {leg.flag ? (
            <div className="flag">
              <div>
                <b>Heads up</b>
                {leg.flag}
              </div>
            </div>
          ) : null}
        </article>
      ))}
    </>
  );
}

function PackingPanel({ trip, api }: { trip: Trip; api: TripApi }) {
  const items = trip.packing.flatMap((section) => section.items);
  const done = items.filter((item) => item.checked).length;
  return (
    <>
      <Progress
        label={`${done} / ${items.length} packed`}
        total={items.length}
        done={done}
      />
      {trip.packing.map((section) => (
        <article key={section.id} className="pack-card">
          <h2 className="section-title">{section.title}</h2>
          {section.items.map((item) => (
            <CheckRow
              key={item.id}
              id={item.id}
              label={item.body}
              checked={item.checked}
              onChange={(checked) => api.togglePacking(item.id, checked)}
            />
          ))}
        </article>
      ))}
      <div className="reset-row">
        <button type="button" onClick={api.resetPacking}>
          Reset packing checkboxes
        </button>
      </div>
    </>
  );
}

function TipsPanel({ trip }: { trip: Trip }) {
  return (
    <>
      {trip.tips.map((tip) => (
        <article key={tip.id} className="tip-card">
          <h4>{tip.title}</h4>
          <p>{tip.body}</p>
        </article>
      ))}
    </>
  );
}

function NotesPanel({ trip, api }: { trip: Trip; api: TripApi }) {
  const [shopText, setShopText] = useState("");
  const [description, setDescription] = useState("");
  const [amount, setAmount] = useState("");
  const [currency, setCurrency] = useState<ExpenseInput["currency"]>("JPY");
  const [category, setCategory] =
    useState<ExpenseInput["category"]>("Shopping");

  const totals = trip.expenses.reduce<Record<string, number>>(
    (sum, expense) => {
      sum[expense.currency] = (sum[expense.currency] ?? 0) + expense.amount;
      return sum;
    },
    {},
  );

  function submitShop() {
    const text = shopText.trim();
    if (!text) return;
    api.addShopping(text);
    setShopText("");
  }

  function submitExpense() {
    const parsed = Number(amount);
    if (!description.trim() || !Number.isFinite(parsed) || parsed <= 0) return;
    api.addExpense({
      description: description.trim(),
      amount: parsed,
      currency,
      category,
    });
    setDescription("");
    setAmount("");
  }

  return (
    <>
      <h2 className="section-title">Shopping list</h2>
      <div className="add-row">
        <input
          value={shopText}
          onChange={(event) => setShopText(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter") submitShop();
          }}
          placeholder="Add an item..."
          aria-label="Shopping item"
        />
        <button type="button" onClick={submitShop}>
          Add
        </button>
      </div>
      {trip.shopping.length === 0 ? (
        <div className="empty-state">No items yet.</div>
      ) : (
        trip.shopping.map((item) => (
          <div
            key={item.id}
            className={item.done ? "note-item done" : "note-item"}
          >
            <input
              id={`shop-${item.id}`}
              type="checkbox"
              checked={item.done}
              onChange={(event) =>
                api.toggleShopping(item.id, event.target.checked)
              }
            />
            <label htmlFor={`shop-${item.id}`}>{item.text}</label>
            <button
              type="button"
              className="del-btn"
              aria-label="Remove"
              onClick={() => api.deleteShopping(item.id)}
            >
              ×
            </button>
          </div>
        ))
      )}

      <h2 className="section-title section-gap">Expense tracker</h2>
      {Object.keys(totals).length === 0 ? (
        <div className="empty-state">No expenses logged yet.</div>
      ) : (
        <div className="totals-row">
          {Object.entries(totals).map(([code, value]) => (
            <div key={code} className="total-chip">
              <div className="tc-currency">{code} total</div>
              <div className="tc-amount">{formatMoney(code, value)}</div>
            </div>
          ))}
        </div>
      )}
      <div className="add-row expense-add-row">
        <input
          value={description}
          onChange={(event) => setDescription(event.target.value)}
          placeholder="What did you spend on?"
          aria-label="Expense description"
        />
        <input
          value={amount}
          onChange={(event) => setAmount(event.target.value)}
          placeholder="Amount"
          inputMode="decimal"
          aria-label="Amount"
          onKeyDown={(event) => {
            if (event.key === "Enter") submitExpense();
          }}
        />
        <select
          value={currency}
          aria-label="Currency"
          onChange={(event) =>
            setCurrency(event.target.value as ExpenseInput["currency"])
          }
        >
          <option value="JPY">¥ JPY</option>
          <option value="PHP">₱ PHP</option>
          <option value="USD">$ USD</option>
        </select>
        <select
          value={category}
          aria-label="Category"
          onChange={(event) =>
            setCategory(event.target.value as ExpenseInput["category"])
          }
        >
          {[
            "Shopping",
            "Food",
            "Transport",
            "Hotel",
            "Activities",
            "Other",
          ].map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
        <button type="button" onClick={submitExpense}>
          Add
        </button>
      </div>
      {trip.expenses.map((expense) => (
        <div key={expense.id} className="expense-item">
          <div className="exp-info">
            <div className="exp-desc">{expense.description}</div>
            <div className="exp-cat">{expense.category}</div>
          </div>
          <div className="exp-amount">
            {formatMoney(expense.currency, expense.amount)}
          </div>
          <button
            type="button"
            className="del-btn"
            aria-label="Remove"
            onClick={() => api.deleteExpense(expense.id)}
          >
            ×
          </button>
        </div>
      ))}
    </>
  );
}

function Progress({
  label,
  total,
  done,
}: {
  label: string;
  total: number;
  done: number;
}) {
  const width = total ? `${(done / total) * 100}%` : "0%";
  return (
    <div className="progress-strip">
      <span>{label}</span>
      <div className="progress-track">
        <div className="progress-fill" style={{ width }} />
      </div>
    </div>
  );
}

function CheckRow({
  id,
  label,
  checked,
  onChange,
}: {
  id: string;
  label: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
}) {
  return (
    <div className={checked ? "task done" : "task"}>
      <input
        id={id}
        type="checkbox"
        checked={checked}
        onChange={(event) => onChange(event.target.checked)}
      />
      <label htmlFor={id}>{label}</label>
    </div>
  );
}

function FlightRow({ flight }: { flight: Flight }) {
  return (
    <div className="flight-row">
      <span className="fr-route">
        {flight.origin} → {flight.destination}
      </span>
      <span className="fr-time">
        {flight.date_label ? `${flight.date_label} · ` : ""}
        {flight.depart_time} – {flight.arrive_time}
      </span>
    </div>
  );
}

function InlineLeg({ leg }: { leg: TransportLeg }) {
  return (
    <div className="inline-transport">
      <div className="it-head">
        {leg.origin} → {leg.destination}
      </div>
      <div className="it-meta">
        <b>{leg.mode}</b> · {leg.duration}
      </div>
      <div className="it-detail">{leg.detail}</div>
      {leg.detail_extra ? (
        <div className="it-detail" style={{ marginTop: 6 }}>
          {leg.detail_extra}
        </div>
      ) : null}
      {leg.flag ? (
        <div className="it-flag">
          <div>
            <b>Heads up</b>
            {leg.flag}
          </div>
        </div>
      ) : null}
    </div>
  );
}
