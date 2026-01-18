"use client";

import { useState } from "react";
import { X, SlidersHorizontal, ChevronDown, ChevronUp } from "lucide-react";

interface FilterSidebarProps {
	onFilterChange: (filters: Filters) => void;
	isOpen: boolean;
	onClose: () => void;
}

export interface Filters {
	priceRange: [number, number];
	brands: string[];
	conditions: string[];
	storage: string[];
	features: string[];
}

const brands = ["Apple", "Samsung", "Dell", "HP", "Sony", "Canon", "Bose", "Microsoft", "Razer", "Logitech"];
const conditions = ["New", "Used - Like New", "Refurbished"];
const storageOptions = ["64GB", "128GB", "256GB", "512GB", "1TB", "2TB"];
const features = ["5G", "Wireless Charging", "Fast Charging", "Water Resistant", "Face ID", "Fingerprint"];

export default function FilterSidebar({ onFilterChange, isOpen, onClose }: FilterSidebarProps) {
	const [filters, setFilters] = useState<Filters>({
		priceRange: [0, 10000000],
		brands: [],
		conditions: [],
		storage: [],
		features: [],
	});

	const [expandedSections, setExpandedSections] = useState({
		price: true,
		brands: true,
		condition: true,
		storage: false,
		features: false,
	});

	const toggleSection = (section: keyof typeof expandedSections) => {
		setExpandedSections((prev) => ({ ...prev, [section]: !prev[section] }));
	};

	const handlePriceChange = (index: 0 | 1, value: number) => {
		const newRange: [number, number] = [...filters.priceRange] as [number, number];
		newRange[index] = value;
		const newFilters = { ...filters, priceRange: newRange };
		setFilters(newFilters);
		onFilterChange(newFilters);
	};

	const toggleArrayFilter = (key: keyof Filters, value: string) => {
		const currentArray = filters[key] as string[];
		const newArray = currentArray.includes(value)
			? currentArray.filter((item) => item !== value)
			: [...currentArray, value];

		const newFilters = { ...filters, [key]: newArray };
		setFilters(newFilters);
		onFilterChange(newFilters);
	};

	const clearFilters = () => {
		const resetFilters: Filters = {
			priceRange: [0, 10000000],
			brands: [],
			conditions: [],
			storage: [],
			features: [],
		};
		setFilters(resetFilters);
		onFilterChange(resetFilters);
	};

	const activeFilterCount =
		filters.brands.length +
		filters.conditions.length +
		filters.storage.length +
		filters.features.length;

	const formatPrice = (amount: number) => {
		return new Intl.NumberFormat("en-UG", {
			style: "currency",
			currency: "UGX",
			minimumFractionDigits: 0,
			maximumFractionDigits: 0,
		}).format(amount);
	};

	return (
		<>
			{/* Mobile Backdrop */}
			{isOpen && (
				<div
					className="fixed inset-0 bg-black/50 z-40 lg:hidden"
					onClick={onClose}
				/>
			)}

			{/* Sidebar */}
			<aside
				className={`
					fixed lg:sticky top-0 left-0 h-screen lg:h-auto
					w-80 lg:w-full bg-white
					overflow-y-auto z-50
					transition-transform duration-300
					${isOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"}
					rounded-2xl shadow-card p-6
				`}
			>
				{/* Header */}
				<div className="flex items-center justify-between mb-6">
					<div className="flex items-center gap-2">
						<SlidersHorizontal size={20} className="text-primary-600" />
						<h2 className="text-xl font-bold text-gray-900">Filters</h2>
						{activeFilterCount > 0 && (
							<span className="bg-primary-600 text-white text-xs px-2 py-1 rounded-full">
								{activeFilterCount}
							</span>
						)}
					</div>
					<button
						onClick={onClose}
						className="lg:hidden text-gray-500 hover:text-gray-700"
					>
						<X size={24} />
					</button>
				</div>

				{/* Clear Filters */}
				{activeFilterCount > 0 && (
					<button
						onClick={clearFilters}
						className="w-full mb-4 text-sm text-primary-600 hover:text-primary-700 font-medium"
					>
						Clear All Filters
					</button>
				)}

				{/* Price Range */}
				<FilterSection
					title="Price Range"
					isExpanded={expandedSections.price}
					onToggle={() => toggleSection("price")}
				>
					<div className="space-y-4">
						<div>
							<label className="text-sm text-gray-600">Min Price</label>
							<input
								type="range"
								min="0"
								max="10000000"
								step="100000"
								value={filters.priceRange[0]}
								onChange={(e) => handlePriceChange(0, parseInt(e.target.value))}
								className="w-full"
							/>
							<p className="text-sm font-semibold text-gray-900 mt-1">
								{formatPrice(filters.priceRange[0])}
							</p>
						</div>
						<div>
							<label className="text-sm text-gray-600">Max Price</label>
							<input
								type="range"
								min="0"
								max="10000000"
								step="100000"
								value={filters.priceRange[1]}
								onChange={(e) => handlePriceChange(1, parseInt(e.target.value))}
								className="w-full"
							/>
							<p className="text-sm font-semibold text-gray-900 mt-1">
								{formatPrice(filters.priceRange[1])}
							</p>
						</div>
					</div>
				</FilterSection>

				{/* Brands */}
				<FilterSection
					title="Brand"
					isExpanded={expandedSections.brands}
					onToggle={() => toggleSection("brands")}
				>
					<div className="space-y-2">
						{brands.map((brand) => (
							<label key={brand} className="flex items-center gap-2 cursor-pointer hover:bg-gray-50 p-2 rounded-lg">
								<input
									type="checkbox"
									checked={filters.brands.includes(brand)}
									onChange={() => toggleArrayFilter("brands", brand)}
									className="w-4 h-4 text-primary-600 rounded"
								/>
								<span className="text-sm text-gray-900">{brand}</span>
							</label>
						))}
					</div>
				</FilterSection>

				{/* Condition */}
				<FilterSection
					title="Condition"
					isExpanded={expandedSections.condition}
					onToggle={() => toggleSection("condition")}
				>
					<div className="space-y-2">
						{conditions.map((condition) => (
							<label key={condition} className="flex items-center gap-2 cursor-pointer hover:bg-gray-50 p-2 rounded-lg">
								<input
									type="checkbox"
									checked={filters.conditions.includes(condition)}
									onChange={() => toggleArrayFilter("conditions", condition)}
									className="w-4 h-4 text-primary-600 rounded"
								/>
								<span className="text-sm text-gray-900">{condition}</span>
							</label>
						))}
					</div>
				</FilterSection>

				{/* Storage */}
				<FilterSection
					title="Storage"
					isExpanded={expandedSections.storage}
					onToggle={() => toggleSection("storage")}
				>
					<div className="grid grid-cols-2 gap-2">
						{storageOptions.map((storage) => (
							<button
								key={storage}
								onClick={() => toggleArrayFilter("storage", storage)}
								className={`
									px-3 py-2 rounded-lg text-sm font-medium transition-colors
									${filters.storage.includes(storage)
										? "bg-primary-600 text-white"
										: "bg-gray-100 text-gray-900 hover:bg-gray-200"
									}
								`}
							>
								{storage}
							</button>
						))}
					</div>
				</FilterSection>

				{/* Features */}
				<FilterSection
					title="Features"
					isExpanded={expandedSections.features}
					onToggle={() => toggleSection("features")}
				>
					<div className="flex flex-wrap gap-2">
						{features.map((feature) => (
							<button
								key={feature}
								onClick={() => toggleArrayFilter("features", feature)}
								className={`
									px-3 py-1.5 rounded-full text-xs font-medium transition-colors
									${filters.features.includes(feature)
										? "bg-primary-600 text-white"
										: "bg-gray-100 text-gray-700 hover:bg-gray-200"
									}
								`}
							>
								{feature}
							</button>
						))}
					</div>
				</FilterSection>
			</aside>
		</>
	);
}

function FilterSection({
	title,
	isExpanded,
	onToggle,
	children,
}: {
	title: string;
	isExpanded: boolean;
	onToggle: () => void;
	children: React.ReactNode;
}) {
	return (
		<div className="border-b border-gray-200 py-4">
			<button
				onClick={onToggle}
				className="w-full flex items-center justify-between mb-3"
			>
				<h3 className="font-semibold text-gray-900">{title}</h3>
				{isExpanded ? (
					<ChevronUp size={20} className="text-gray-500" />
				) : (
					<ChevronDown size={20} className="text-gray-500" />
				)}
			</button>
			{isExpanded && <div>{children}</div>}
		</div>
	);
}
