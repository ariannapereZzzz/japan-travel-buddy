export type Flight = {
  origin: string;
  destination: string;
  date_label: string | null;
  depart_time: string;
  arrive_time: string;
};

export type FlightGroup = {
  label: string;
  legs: Flight[];
};

export type Hotel = {
  id: string;
  city: string;
  check_in: string;
  check_out: string;
  nights: number;
};

export type TransportLeg = {
  id: string;
  origin: string;
  destination: string;
  duration: string;
  mode: string;
  detail: string;
  detail_extra: string | null;
  flag: string | null;
};

export type Task = {
  id: string;
  body: string;
  checked: boolean;
};

export type Day = {
  id: string;
  code: string;
  date_label: string;
  title: string;
  subtitle: string;
  transit: string | null;
  flights: Flight[];
  leg: TransportLeg | null;
  tasks: Task[];
};

export type PackingSection = {
  id: string;
  title: string;
  items: { id: string; body: string; checked: boolean }[];
};

export type Trip = {
  slug: string;
  title: string;
  eyebrow: string;
  date_label: string;
  route: string[];
  callout: { title: string; body: string } | null;
  hotels: Hotel[];
  flight_groups: FlightGroup[];
  days: Day[];
  legs: TransportLeg[];
  packing: PackingSection[];
  tips: { id: string; title: string; body: string }[];
  shopping: { id: string; text: string; done: boolean }[];
  expenses: {
    id: string;
    description: string;
    amount: number;
    currency: string;
    category: string;
  }[];
};

export type ExpenseInput = {
  description: string;
  amount: number;
  currency: "JPY" | "PHP" | "USD";
  category:
    "Shopping" | "Food" | "Transport" | "Hotel" | "Activities" | "Other";
};
