require 'pry'
ElementMasses = Hash[File.read("elements").split("\n").map do |x|
                       symbol, mass = x.split(' ')
                       [symbol, mass.to_i]
                     end]

class Fertilizer
  attr_accessor :elements,:formula,:compbymass,:molar_mass
  def initialize(fmla)
    _parse_fmla(fmla)
    @formula = fmla
  end

  def percentages
  end
  def _parse_fmla(fmla)
    @elements = Hash[fmla.scan(/([A-Z][a-z]?)(\d*)/).map do |r|
      element, count = r[0] , r[1] == ""  ? 1 : r[1].to_i
    end]
    @molar_mass = @elements.inject(0) do |tot,x| tot + x[1] * ElementMasses[x[0]] end
          
  end
end
print Fertilizer.new("KNO3").elements
print Fertilizer.new("KNO3").molar_mass

# Input: desired ppm of each element




