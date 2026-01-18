"use client";

import Link from "next/link";
import {
	Smartphone,
	Laptop,
	Gamepad2,
	Camera,
	Headphones,
	Watch,
	Tv,
	Monitor,
	TabletSmartphone,
	Speaker,
	Keyboard,
	Mouse,
	LucideIcon
} from "lucide-react";

interface Category {
	id: string;
	name: string;
	slug: string;
	icon: LucideIcon;
	productCount: number;
	color: string;
}

const categories: Category[] = [
	{ id: "1", name: "Smartphones", slug: "smartphones", icon: Smartphone, productCount: 247, color: "bg-blue-100 text-blue-600" },
	{ id: "2", name: "Laptops", slug: "laptops", icon: Laptop, productCount: 189, color: "bg-purple-100 text-purple-600" },
	{ id: "3", name: "Gaming", slug: "gaming", icon: Gamepad2, productCount: 156, color: "bg-red-100 text-red-600" },
	{ id: "4", name: "Cameras", slug: "cameras", icon: Camera, productCount: 98, color: "bg-green-100 text-green-600" },
	{ id: "5", name: "Audio", slug: "audio", icon: Headphones, productCount: 312, color: "bg-orange-100 text-orange-600" },
	{ id: "6", name: "Smartwatches", slug: "smartwatches", icon: Watch, productCount: 145, color: "bg-pink-100 text-pink-600" },
	{ id: "7", name: "TVs", slug: "tvs", icon: Tv, productCount: 87, color: "bg-indigo-100 text-indigo-600" },
	{ id: "8", name: "Monitors", slug: "monitors", icon: Monitor, productCount: 134, color: "bg-cyan-100 text-cyan-600" },
	{ id: "9", name: "Tablets", slug: "tablets", icon: TabletSmartphone, productCount: 76, color: "bg-yellow-100 text-yellow-600" },
	{ id: "10", name: "Speakers", slug: "speakers", icon: Speaker, productCount: 203, color: "bg-teal-100 text-teal-600" },
	{ id: "11", name: "Keyboards", slug: "keyboards", icon: Keyboard, productCount: 167, color: "bg-lime-100 text-lime-600" },
	{ id: "12", name: "Mice", slug: "mice", icon: Mouse, productCount: 145, color: "bg-rose-100 text-rose-600" },
];

export default function CategoryGrid() {
	return (
		<section className="py-4">
			<div className="flex items-center justify-between mb-4">
				<h2 className="text-xl md:text-2xl font-bold text-gray-900">Shop by Category</h2>
				<Link
					href="/categories"
					className="text-primary-500 hover:text-primary-600 font-semibold text-sm flex items-center gap-1"
				>
					View All
					<span>→</span>
				</Link>
			</div>

			{/* Desktop: Horizontal Scroll Grid */}
			<div className="hidden md:grid md:grid-cols-6 gap-4">
				{categories.map((category) => (
					<CategoryCard key={category.id} category={category} />
				))}
			</div>

			{/* Mobile: Horizontal Scroll */}
			<div className="md:hidden overflow-x-auto pb-4 -mx-4 px-4 scrollbar-hide">
				<div className="flex gap-3" style={{ width: 'max-content' }}>
					{categories.map((category) => (
						<CategoryCard key={category.id} category={category} mobile />
					))}
				</div>
			</div>
		</section>
	);
}

function CategoryCard({ category, mobile = false }: { category: Category; mobile?: boolean }) {
	const Icon = category.icon;

	return (
		<Link
			href={`/products/${category.slug}`}
			className={`
				group bg-white rounded-xl p-3 shadow-sm hover:shadow-md border border-gray-100
				transition-all duration-300 hover:-translate-y-0.5
				${mobile ? 'w-24 flex-shrink-0' : ''}
			`}
		>
			<div className="flex flex-col items-center text-center">
				{/* Icon */}
				<div
					className={`
						w-14 h-14 rounded-xl flex items-center justify-center mb-2
						group-hover:scale-110 transition-transform duration-300
						${category.color}
					`}
				>
					<Icon size={28} strokeWidth={2} />
				</div>

				{/* Name */}
				<h3 className="font-semibold text-gray-900 text-xs mb-0.5 group-hover:text-primary-500 transition-colors">
					{category.name}
				</h3>

				{/* Product Count */}
				<p className="text-[10px] text-gray-500">
					{category.productCount} items
				</p>
			</div>
		</Link>
	);
}
