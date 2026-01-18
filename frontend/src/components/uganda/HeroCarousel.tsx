"use client";

import { useState, useEffect } from "react";
import Image from "next/image";
import Link from "next/link";
import { ChevronLeft, ChevronRight } from "lucide-react";

interface Slide {
	id: string;
	title: string;
	subtitle: string;
	image: string;
	cta: {
		text: string;
		href: string;
	};
	badge?: string;
}

interface HeroCarouselProps {
	slides: Slide[];
	autoPlay?: boolean;
	interval?: number;
}

export default function HeroCarousel({
	slides,
	autoPlay = true,
	interval = 5000,
}: HeroCarouselProps) {
	const [currentIndex, setCurrentIndex] = useState(0);

	useEffect(() => {
		if (!autoPlay) return;

		const timer = setInterval(() => {
			setCurrentIndex((prev) => (prev + 1) % slides.length);
		}, interval);

		return () => clearInterval(timer);
	}, [autoPlay, interval, slides.length]);

	const goToPrevious = () => {
		setCurrentIndex((prev) => (prev - 1 + slides.length) % slides.length);
	};

	const goToNext = () => {
		setCurrentIndex((prev) => (prev + 1) % slides.length);
	};

	const goToSlide = (index: number) => {
		setCurrentIndex(index);
	};

	return (
		<div className="relative w-full h-[400px] md:h-[500px] rounded-3xl overflow-hidden bg-gradient-to-br from-primary-600 to-primary-800 shadow-xl">
			{/* Slides */}
			<div className="relative w-full h-full">
				{slides.map((slide, index) => (
					<div
						key={slide.id}
						className={`absolute inset-0 transition-opacity duration-500 ${
							index === currentIndex ? "opacity-100" : "opacity-0"
						}`}
					>
						{/* Background Image */}
						<Image
							src={slide.image}
							alt={slide.title}
							fill
							className="object-cover"
							priority={index === 0}
						/>

						{/* Gradient Overlay */}
						<div className="absolute inset-0 bg-gradient-to-r from-black/60 to-transparent" />

						{/* Content */}
						<div className="relative z-10 h-full flex items-center">
							<div className="container mx-auto px-4 md:px-8">
								<div className="max-w-2xl">
									{slide.badge && (
										<span className="inline-block bg-accent-500 text-white px-4 py-1.5 rounded-full text-sm font-bold mb-4 animate-bounce-slow">
											{slide.badge}
										</span>
									)}
									<h1 className="text-4xl md:text-6xl font-bold text-white mb-4 animate-slide-up">
										{slide.title}
									</h1>
									<p className="text-lg md:text-xl text-white/90 mb-8 animate-slide-up">
										{slide.subtitle}
									</p>
									<Link
										href={slide.cta.href}
										className="inline-block bg-white text-primary-600 px-8 py-4 rounded-xl font-bold text-lg hover:bg-primary-50 transition-colors shadow-lg hover:shadow-xl animate-slide-up"
									>
										{slide.cta.text}
									</Link>
								</div>
							</div>
						</div>
					</div>
				))}
			</div>

			{/* Navigation Arrows */}
			<button
				onClick={goToPrevious}
				className="absolute left-4 top-1/2 -translate-y-1/2 w-12 h-12 bg-white/10 backdrop-blur-md hover:bg-white/20 rounded-full flex items-center justify-center transition-all z-20 group"
				aria-label="Previous slide"
			>
				<ChevronLeft className="text-white group-hover:scale-110 transition-transform" size={28} />
			</button>
			<button
				onClick={goToNext}
				className="absolute right-4 top-1/2 -translate-y-1/2 w-12 h-12 bg-white/10 backdrop-blur-md hover:bg-white/20 rounded-full flex items-center justify-center transition-all z-20 group"
				aria-label="Next slide"
			>
				<ChevronRight className="text-white group-hover:scale-110 transition-transform" size={28} />
			</button>

			{/* Dots Indicator */}
			<div className="absolute bottom-6 left-1/2 -translate-x-1/2 flex gap-2 z-20">
				{slides.map((_, index) => (
					<button
						key={index}
						onClick={() => goToSlide(index)}
						className={`h-2 rounded-full transition-all ${
							index === currentIndex
								? "w-8 bg-white"
								: "w-2 bg-white/50 hover:bg-white/75"
						}`}
						aria-label={`Go to slide ${index + 1}`}
					/>
				))}
			</div>
		</div>
	);
}
